import { ref } from 'vue'
import { useRole } from './useRole'

function resolveRouteFromLocation() {
  if (typeof window === 'undefined') return 'landing'
  return window.location.pathname.startsWith('/workspace') ? 'workspace' : 'landing'
}

const currentRoute = ref(resolveRouteFromLocation())
let initialized = false

export function useNavigation() {
  const { setRole } = useRole()

  if (!initialized && typeof window !== 'undefined') {
    window.addEventListener('popstate', () => {
      currentRoute.value = resolveRouteFromLocation()
    })
    initialized = true
  }

  function goToLanding() {
    currentRoute.value = 'landing'
    if (typeof window !== 'undefined') {
      if (window.location.pathname !== '/') {
        window.history.pushState({}, '', '/')
      }
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  function goToWorkspace(roleCode) {
    if (roleCode) {
      setRole(roleCode)
    }
    currentRoute.value = 'workspace'
    if (typeof window !== 'undefined') {
      if (!window.location.pathname.startsWith('/workspace')) {
        window.history.pushState({}, '', '/workspace')
      }
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  return {
    currentRoute,
    goToLanding,
    goToWorkspace,
  }
}
