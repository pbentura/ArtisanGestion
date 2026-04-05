import { useDark, useToggle } from '@vueuse/core'

const isDark = useDark({
  selector: 'html',
  attribute: 'class',
  valueDark: 'dark',
  valueLight: '',
  storageKey: 'ventura-theme',
})

const toggleDark = useToggle(isDark)

export function useTheme() {
  return {
    isDark,
    toggleDark,
  }
}
