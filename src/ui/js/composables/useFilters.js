import { ref, watch } from 'vue'
import { router } from '@inertiajs/vue3'

export function useFilters(initialFilters = {}, url) {
  const filters = ref({ ...initialFilters })

  let debounceTimer = null

  function applyFilters(immediate = false) {
    const apply = () => {
      const params = {}
      for (const [key, val] of Object.entries(filters.value)) {
        if (val !== '' && val !== null && val !== undefined) {
          params[key] = val
        }
      }
      router.get(url, params, {
        preserveState: true,
        replace: true,
        preserveScroll: true,
      })
    }

    if (immediate) {
      apply()
    } else {
      clearTimeout(debounceTimer)
      debounceTimer = setTimeout(apply, 300)
    }
  }

  function resetFilters() {
    for (const key of Object.keys(filters.value)) {
      filters.value[key] = ''
    }
    applyFilters(true)
  }

  return { filters, applyFilters, resetFilters }
}
