export const AUTHENTICATION_REQUIRED_EVENT = 'authentication-required'

export async function authFetch(input, options = {}) {
  const { suppressAuthenticationRedirect = false, ...fetchOptions } = options
  const response = await fetch(input, fetchOptions)

  if (!suppressAuthenticationRedirect && (response.status === 401 || response.status === 403)) {
    window.dispatchEvent(new Event(AUTHENTICATION_REQUIRED_EVENT))
  }

  return response
}
