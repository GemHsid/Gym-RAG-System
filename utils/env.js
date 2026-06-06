const ENV_BASE_URL_MAP = {
  develop: 'http://127.0.0.1:8000/api',
  trial: 'https://api-trial.example.com/api',
  release: 'https://api.example.com/api'
}

function isPlaceholderBaseUrl(url = '') {
  return /example\.com/i.test(String(url))
}

function getEnvVersion() {
  const accountInfo = wx.getAccountInfoSync ? wx.getAccountInfoSync() : null
  const miniProgram = accountInfo && accountInfo.miniProgram ? accountInfo.miniProgram : {}
  return miniProgram.envVersion || 'develop'
}

function normalizeBaseUrl(url = '') {
  return String(url).replace(/\/+$/, '')
}

function getApiBaseUrl() {
  const customBaseUrl = wx.getStorageSync('customApiBaseUrl')
  if (customBaseUrl) {
    return normalizeBaseUrl(customBaseUrl)
  }
  const envVersion = getEnvVersion()
  return normalizeBaseUrl(ENV_BASE_URL_MAP[envVersion] || ENV_BASE_URL_MAP.develop)
}

function isCurrentBaseUrlPlaceholder() {
  const customBaseUrl = wx.getStorageSync('customApiBaseUrl')
  if (customBaseUrl) {  
    return false
  }
  const envVersion = getEnvVersion()
  const baseUrl = ENV_BASE_URL_MAP[envVersion] || ENV_BASE_URL_MAP.develop
  if (envVersion === 'develop') {
    return false
  }
  return isPlaceholderBaseUrl(baseUrl)
}

function setCustomApiBaseUrl(url = '') {
  const normalized = normalizeBaseUrl(url)
  if (!normalized) {
    wx.removeStorageSync('customApiBaseUrl')
    return ''
  }
  wx.setStorageSync('customApiBaseUrl', normalized)
  return normalized
}

module.exports = {
  ENV_BASE_URL_MAP,
  getEnvVersion,
  getApiBaseUrl,
  setCustomApiBaseUrl,
  isPlaceholderBaseUrl,
  isCurrentBaseUrlPlaceholder
}
