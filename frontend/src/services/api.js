import { useRole } from '../composables/useRole'

const BASE_URL = '/api'

export class ApiError extends Error {
  constructor(message, { status = 0, code = 'API_ERROR', isNetworkOrGateway = false } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.isNetworkOrGateway = isNetworkOrGateway
  }
}

/**
 * Execute an HTTP request against /api with automatic X-User-Role header.
 * Parses standard SIUDES JSON: { success: bool, data: any, error: { code, message } | null }.
 */
export async function apiRequest(path, options = {}) {
  const { activeRole } = useRole()
  const url = `${BASE_URL}${path.startsWith('/') ? path : `/${path}`}`

  const headers = {
    Accept: 'application/json',
    'X-User-Role': activeRole.value,
    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
    ...(options.headers || {}),
  }

  let response
  try {
    response = await fetch(url, {
      ...options,
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    })
  } catch (err) {
    throw new ApiError('Tidak dapat terhubung ke server API.', {
      status: 0,
      code: 'NETWORK_ERROR',
      isNetworkOrGateway: true,
    })
  }

  const contentType = response.headers.get('content-type') || ''
  if (!contentType.includes('application/json')) {
    throw new ApiError(
      `Layanan belum tersedia (HTTP ${response.status}).`,
      {
        status: response.status,
        code: 'BAD_GATEWAY',
        isNetworkOrGateway: response.status >= 500 || response.status === 404,
      }
    )
  }

  const payload = await response.json()
  if (!response.ok || payload?.success === false) {
    throw new ApiError(
      payload?.error?.message || `Permintaan gagal (HTTP ${response.status}).`,
      {
        status: response.status,
        code: payload?.error?.code || 'HTTP_ERROR',
        isNetworkOrGateway: response.status >= 502,
      }
    )
  }

  return payload.data
}

export function getUnitMaster() {
  return apiRequest('/unit/master', { method: 'GET' })
}

export function postUnitUsage({ customer_code, unit_type, usage_amount }) {
  return apiRequest('/unit/usage', {
    method: 'POST',
    body: { customer_code, unit_type, usage_amount },
  })
}
