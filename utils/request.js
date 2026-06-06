const { getAccessToken, getRefreshToken, saveAuth, clearAuth } = require('./auth')
const { getApiBaseUrl, setCustomApiBaseUrl, isCurrentBaseUrlPlaceholder } = require('./env')
let refreshingPromise = null

function joinUrl(path = '') {
  const API_BASE_URL = getApiBaseUrl()
  if (/^https?:\/\//.test(path)) {
    return path
  }
  const normalizedBase = API_BASE_URL.replace(/\/+$/, '')
  const normalizedPath = String(path).replace(/^\/+/, '')
  return `${normalizedBase}/${normalizedPath}`
}

function normalizeError(message, code) {
  return {
    code: code || -1,
    message: message || '请求失败'
  }
}

function syncAppAuthState() {
  if (typeof getApp !== 'function') {
    return
  }
  try {
    const app = getApp()
    if (!app || !app.globalData || !app.globalData.auth) {
      return
    }
    app.globalData.auth.accessToken = getAccessToken()
    app.globalData.auth.refreshToken = getRefreshToken()
  } catch (e) {
    return
  }
}

function refreshAccessToken() {
  if (refreshingPromise) {
    return refreshingPromise
  }
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    return Promise.reject(normalizeError('登录已失效，请重新登录', 401))
  }

  refreshingPromise = request({
    url: 'users/token/refresh/',
    method: 'POST',
    data: { refresh: refreshToken },
    needAuth: false,
    __skipAuthRefresh: true
  })
    .then((result) => {
      const access = result && result.access
      if (!access) {
        throw normalizeError('刷新失败：未返回新token', 401)
      }
      saveAuth({
        access,
        refresh: refreshToken
      })
      syncAppAuthState()
      return access
    })
    .finally(() => {
      refreshingPromise = null
    })

  return refreshingPromise
}

function reloginIfPossible() {
  if (typeof getApp !== 'function') {
    return Promise.reject(normalizeError('登录已失效，请重新登录', 401))
  }
  
  // 自动跳转到登录页
  wx.navigateTo({
    url: '/pages/login/login'
  })
  
  return Promise.reject(normalizeError('登录已失效，请重新登录', 401))
}

function request(options = {}) {
  const {
    url = '',
    method = 'GET',
    data = {},
    header = {},
    needAuth = true,
    timeout = 10000,
    __retried = false,
    __skipAuthRefresh = false
  } = options

  return new Promise((resolve, reject) => {
    const accessToken = getAccessToken()
    const requestHeader = {
      'Content-Type': 'application/json',
      ...header
    }

    if (needAuth && accessToken) {
      requestHeader.Authorization = `Bearer ${accessToken}`
    }

    wx.request({
      url: joinUrl(url),
      method,
      data,
      timeout,
      header: requestHeader,
      success: (res) => {
        const statusCode = res.statusCode || 0
        const payload = res.data || {}
        const businessCode = payload.code
        const unauthorized = statusCode === 401 || businessCode === 401

        if (statusCode >= 200 && statusCode < 300 && businessCode === 0) {
          resolve(payload.data)
          return
        }

        if (needAuth && unauthorized && !__retried && !__skipAuthRefresh) {
          refreshAccessToken()
            .catch(() => {
              clearAuth()
              syncAppAuthState()
              return reloginIfPossible()
            })
            .then(() => request({
              ...options,
              __retried: true,
              __skipAuthRefresh: true
            }))
            .then(resolve)
            .catch((refreshErr) => {
              reject(normalizeError((refreshErr && refreshErr.message) || '登录已失效，请重新登录', 401))
            })
          return
        }

        const errorCode = businessCode || statusCode
        const errorMessage = payload.message || '请求失败'
        reject(normalizeError(errorMessage, errorCode))
      },
      fail: (err) => {
        const rawMessage = err && err.errMsg ? err.errMsg : ''
        let errorMessage = rawMessage ? `网络异常：${rawMessage}` : '网络异常，请稍后重试'
        if (/not in domain list/i.test(rawMessage)) {
          errorMessage = '网络异常：请求域名未加入小程序合法域名白名单'
        } else if (/timeout/i.test(rawMessage)) {
          errorMessage = '网络异常：请求超时，请检查网络或后端服务'
        } else if (/fail ssl handshake/i.test(rawMessage)) {
          errorMessage = '网络异常：HTTPS证书或握手异常'
        }
        reject(normalizeError(errorMessage))
      }
    })
  })
}

function get(url, data = {}, options = {}) {
  return request({
    ...options,
    url,
    method: 'GET',
    data
  })
}

function post(url, data = {}, options = {}) {
  return request({
    ...options,
    url,
    method: 'POST',
    data
  })
}

module.exports = {
  getApiBaseUrl,
  setCustomApiBaseUrl,
  request,
  get,
  post
}
