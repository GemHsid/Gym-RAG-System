const { post, getApiBaseUrl, setCustomApiBaseUrl, isCurrentBaseUrlPlaceholder } = require('./utils/request')
const { saveAuth, getAuthState, getAccessToken, hasRealOpenId, clearAuth } = require('./utils/auth')

App({
  onLaunch() {
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    this.hydrateAuth()
    this.ensureLogin()
    this.refreshApiBaseUrl()
  },

  hydrateAuth() {
    this.globalData.auth = getAuthState()
    return this.globalData.auth
  },

  ensureLogin(force = false) {
    if (!force) {
      const cachedAccessToken = getAccessToken()
      if (cachedAccessToken) {
        this.globalData.auth = getAuthState()
        return Promise.resolve(this.globalData.auth)
      }
    }

    return new Promise((resolve, reject) => {
      wx.login({
        success: (loginRes) => {
          const code = loginRes.code
          if (!code) {
            reject({ code: -1, message: '微信登录失败' })
            return
          }

          post('users/login/', { code }, { needAuth: false })
            .then((authData) => {
              saveAuth(authData || {})
              this.globalData.auth = getAuthState()
              this.globalData.openIdCheckPassed = hasRealOpenId(this.globalData.auth)
              resolve(this.globalData.auth)
            })
            .catch((err) => {
              clearAuth()
              this.globalData.auth = getAuthState()
              this.globalData.openIdCheckPassed = false
              reject(err)
            })
        },
        fail: () => {
          reject({ code: -1, message: '微信登录失败' })
        }
      })
    })
  },

  logout() {
    clearAuth()
    this.globalData.auth = getAuthState()
    this.globalData.openIdCheckPassed = false
  },

  hasRealOpenId() {
    const authState = getAuthState()
    this.globalData.auth = authState
    const passed = hasRealOpenId(authState)
    this.globalData.openIdCheckPassed = passed
    return passed
  },

  ensureRealOpenId() {
    const passed = this.hasRealOpenId()
    if (!passed) {
      const authState = getAuthState()
      if (authState && authState.accessToken) {
        return true
      }
      wx.showToast({
        title: '当前登录未完成真实OpenID校验',
        icon: 'none'
      })
    }
    return passed
  },

  refreshApiBaseUrl() {
    this.globalData.apiBaseUrl = `${getApiBaseUrl()}/`
    return this.globalData.apiBaseUrl
  },

  setApiBaseUrl(url = '') {
    setCustomApiBaseUrl(url)
    return this.refreshApiBaseUrl()
  },

  globalData: {
    userInfo: null,
    auth: {
      accessToken: '',
      refreshToken: '',
      userId: null,
      nickname: '',
      openId: '',
      openIdReady: false
    },
    apiBaseUrl: `${getApiBaseUrl()}/`,
    openIdCheckPassed: false
  }
})
