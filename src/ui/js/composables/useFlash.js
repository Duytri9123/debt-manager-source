import { watch } from 'vue'
import { usePage } from '@inertiajs/vue3'

export function useFlash(callback) {
  const page = usePage()
  watch(
    () => page.props.flash,
    (flash) => {
      if (flash?.success) callback(flash.success, 'success')
      if (flash?.error)   callback(flash.error, 'error')
    },
    { immediate: true, deep: true }
  )
}
