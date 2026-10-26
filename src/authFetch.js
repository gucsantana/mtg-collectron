export const AUTHENTICATION_REQUIRED_EVENT = 'authentication-required'

export async function authFetch(...args) {
  const response = await fetch(...args)

  if (response.status === 401 || response.status === 403) {
    window.dispatchEvent(new Event(AUTHENTICATION_REQUIRED_EVENT))
  }

  return response
}
