/**
 * Export invoice to Excel or PDF
 * Uses xlsx for Excel, jsPDF + jspdf-autotable for PDF
 */

export function formatVND(v) {
    return Number(v || 0).toLocaleString('vi-VN', { style: 'currency', currency: 'VND' })
}

/**
 * Export invoice to Excel (.xlsx)
 * @param {Object} invoice - Invoice data with items
 * @param {string} type - 'purchase' | 'sales'
 */
export async function exportToExcel(invoice, type = 'purchase') {
    const XLSX = await import('xlsx')

    const title = type === 'purchase' ? 'HÓA ĐƠN NHẬP HÀNG' : 'HÓA ĐƠN BÁN HÀNG'
    const counterpart = type === 'purchase'
        ? (invoice.supplier?.name ?? '—')
        : (invoice.customer?.name ?? '—')
    const counterpartLabel = type === 'purchase' ? 'Nhà cung cấp' : 'Khách hàng'

    // Header rows
    const headerRows = [
        [title],
        ['Số hóa đơn:', invoice.invoice_number],
        [counterpartLabel + ':', counterpart],
        ['Ngày:', new Date(invoice.invoice_date).toLocaleDateString('vi-VN')],
        ['Trạng thái:', invoice.status],
        [],
        // Table header
        ['STT', 'Tên hàng hóa', 'ĐVT', 'Số lượng', 'Đơn giá', 'Thuế (%)', 'CK (%)', 'Thành tiền'],
    ]

    // Item rows
    const itemRows = (invoice.items ?? []).map((item, i) => [
        i + 1,
        item.product_name,
        item.unit ?? '',
        Number(item.quantity),
        Number(item.unit_price),
        Number(item.tax_rate ?? 0),
        Number(item.discount_rate ?? 0),
        Number(item.total_price),
    ])

    // Summary rows
    const summaryRows = [
        [],
        ['', '', '', '', '', '', 'Tạm tính:', Number(invoice.subtotal ?? 0)],
        ['', '', '', '', '', '', 'Thuế:', Number(invoice.tax_amount ?? 0)],
        ['', '', '', '', '', '', 'Chiết khấu:', Number(invoice.discount_amount ?? 0)],
        ['', '', '', '', '', '', 'TỔNG CỘNG:', Number(invoice.total_amount ?? 0)],
        ['', '', '', '', '', '', 'Đã thanh toán:', Number(invoice.paid_amount ?? 0)],
        ['', '', '', '', '', '', 'Còn lại:', Number(invoice.total_amount ?? 0) - Number(invoice.paid_amount ?? 0)],
    ]

    const allRows = [...headerRows, ...itemRows, ...summaryRows]

    const ws = XLSX.utils.aoa_to_sheet(allRows)

    // Column widths
    ws['!cols'] = [
        { wch: 5 }, { wch: 35 }, { wch: 8 }, { wch: 10 },
        { wch: 15 }, { wch: 10 }, { wch: 10 }, { wch: 18 },
    ]

    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Hóa đơn')

    const filename = `${invoice.invoice_number}_${new Date().toISOString().split('T')[0]}.xlsx`
    XLSX.writeFile(wb, filename)
}

/**
 * Export invoice to PDF
 * @param {Object} invoice - Invoice data with items
 * @param {string} type - 'purchase' | 'sales'
 */
export async function exportToPDF(invoice, type = 'purchase') {
    const { default: jsPDF } = await import('jspdf')
    const { default: autoTable } = await import('jspdf-autotable')

    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })

    const title = type === 'purchase' ? 'HÓA ĐƠN NHẬP HÀNG' : 'HÓA ĐƠN BÁN HÀNG'
    const counterpart = type === 'purchase'
        ? (invoice.supplier?.name ?? '—')
        : (invoice.customer?.name ?? '—')
    const counterpartLabel = type === 'purchase' ? 'Nha cung cap' : 'Khach hang'

    // Title
    doc.setFontSize(18)
    doc.setFont('helvetica', 'bold')
    doc.text(title, 105, 20, { align: 'center' })

    // Info
    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    const infoY = 32
    doc.text(`So hoa don: ${invoice.invoice_number}`, 14, infoY)
    doc.text(`${counterpartLabel}: ${counterpart}`, 14, infoY + 6)
    doc.text(`Ngay: ${new Date(invoice.invoice_date).toLocaleDateString('vi-VN')}`, 14, infoY + 12)
    doc.text(`Trang thai: ${invoice.status}`, 14, infoY + 18)

    // Table
    const tableData = (invoice.items ?? []).map((item, i) => [
        i + 1,
        item.product_name,
        item.unit ?? '',
        Number(item.quantity).toLocaleString(),
        formatVND(item.unit_price),
        `${item.tax_rate ?? 0}%`,
        `${item.discount_rate ?? 0}%`,
        formatVND(item.total_price),
    ])

    autoTable(doc, {
        startY: infoY + 26,
        head: [['STT', 'Ten hang hoa', 'DVT', 'So luong', 'Don gia', 'Thue', 'CK', 'Thanh tien']],
        body: tableData,
        styles: { fontSize: 9, cellPadding: 2 },
        headStyles: { fillColor: [79, 70, 229], textColor: 255, fontStyle: 'bold' },
        alternateRowStyles: { fillColor: [248, 250, 252] },
        columnStyles: {
            0: { halign: 'center', cellWidth: 10 },
            1: { cellWidth: 55 },
            2: { halign: 'center', cellWidth: 15 },
            3: { halign: 'right', cellWidth: 18 },
            4: { halign: 'right', cellWidth: 25 },
            5: { halign: 'center', cellWidth: 12 },
            6: { halign: 'center', cellWidth: 12 },
            7: { halign: 'right', cellWidth: 28 },
        },
    })

    // Summary
    const finalY = doc.lastAutoTable.finalY + 8
    doc.setFontSize(10)
    const summaryX = 140

    const summaryLines = [
        ['Tam tinh:', formatVND(invoice.subtotal ?? 0)],
        ['Thue:', formatVND(invoice.tax_amount ?? 0)],
        ['Chiet khau:', formatVND(invoice.discount_amount ?? 0)],
    ]

    summaryLines.forEach(([label, value], i) => {
        doc.text(label, summaryX, finalY + i * 6)
        doc.text(value, 196, finalY + i * 6, { align: 'right' })
    })

    // Total
    doc.setFont('helvetica', 'bold')
    doc.setFontSize(11)
    doc.text('TONG CONG:', summaryX, finalY + 20)
    doc.text(formatVND(invoice.total_amount ?? 0), 196, finalY + 20, { align: 'right' })

    doc.setFont('helvetica', 'normal')
    doc.setFontSize(9)
    doc.text(`Da thanh toan: ${formatVND(invoice.paid_amount ?? 0)}`, summaryX, finalY + 27)
    doc.text(`Con lai: ${formatVND((invoice.total_amount ?? 0) - (invoice.paid_amount ?? 0))}`, summaryX, finalY + 33)

    const filename = `${invoice.invoice_number}_${new Date().toISOString().split('T')[0]}.pdf`
    doc.save(filename)
}
