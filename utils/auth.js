const ACCESS_TOKEN_KEY = 'accessToken'
const REFRESH_TOKEN_KEY = 'refreshToken'
const USER_ID_KEY = 'userId'
const NICKNAME_KEY = 'nickname'
const OPEN_ID_KEY = 'openId'
const OPEN_ID_READY_KEY = 'openIdReady'

function saveAuth(authData = {}) {
  const {
    access,
    refresh,
    user_id: userId,
    nickname,
    openid,
    open_id: openIdAlias,
    is_mock_openid: isMockOpenId
  } = authData
  const openId = openid || openIdAlias || ''
  const hasOpenIdField = Object.prototype.hasOwnProperty.call(authData, 'openid')
    || Object.prototype.hasOwnProperty.call(authData, 'open_id')
  const hasMockFlag = Object.prototype.hasOwnProperty.call(authData, 'is_mock_openid')
  const openIdReady = !!openId && !isMockOpenId && !/^mock[_-]/i.test(String(openId))
  if (access) {
    wx.setStorageSync(ACCESS_TOKEN_KEY, access)
  }
  if (refresh) {
    wx.setStorageSync(REFRESH_TOKEN_KEY, refresh)
  }
  if (userId !== undefined && userId !== null) {
    wx.setStorageSync(USER_ID_KEY, userId)
  }
  if (nickname) {
    wx.setStorageSync(NICKNAME_KEY, nickname)
  }
  if (openId) {
    wx.setStorageSync(OPEN_ID_KEY, openId)
  }
  if (hasOpenIdField || hasMockFlag) {
    wx.setStorageSync(OPEN_ID_READY_KEY, openIdReady)
  }
}

function getAccessToken() {
  return wx.getStorageSync(ACCESS_TOKEN_KEY) || ''
}

function getRefreshToken() {
  return wx.getStorageSync(REFRESH_TOKEN_KEY) || ''
}

function getAuthState() {
  return {
    accessToken: getAccessToken(),
    refreshToken: getRefreshToken(),
    userId: wx.getStorageSync(USER_ID_KEY) || null,
    nickname: wx.getStorageSync(NICKNAME_KEY) || '',
    openId: wx.getStorageSync(OPEN_ID_KEY) || '',
    openIdReady: !!wx.getStorageSync(OPEN_ID_READY_KEY)
  }
}

function hasRealOpenId(authState = getAuthState()) {
  return !!(authState.openId && authState.openIdReady)
}

function clearAuth() {
  wx.removeStorageSync(ACCESS_TOKEN_KEY)
  wx.removeStorageSync(REFRESH_TOKEN_KEY)
  wx.removeStorageSync(USER_ID_KEY)
  wx.removeStorageSync(NICKNAME_KEY)
  wx.removeStorageSync(OPEN_ID_KEY)
  wx.removeStorageSync(OPEN_ID_READY_KEY)
}

module.exports = {
  saveAuth,
  getAccessToken,
  getRefreshToken,
  getAuthState,
  hasRealOpenId,
  clearAuth
}
