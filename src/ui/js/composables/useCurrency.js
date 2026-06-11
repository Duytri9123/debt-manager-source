export function useCurrency() {
  function formatVND(amount) {
    if (amount === null || amount === undefined) return '0 ₫'
    return Number(amount).toLocaleString('vi-VN', {
      style: 'currency',
      currency: 'VND',
    })
  }

  function formatNumber(amount) {
    if (amount === null || amount === undefined) return '0'
    return Number(amount).toLocaleString('vi-VN')
  }

  return { formatVND, formatNumber }
}
