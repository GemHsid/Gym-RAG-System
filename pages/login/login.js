// pages/login/login.js
const { post } = require('../../utils/request')
const { saveAuth } = require('../../utils/auth')

Page({
  data: {
    isAgreed: false,
    loading: false,
    logoSrc: '/首页图像/LOGO.png'
  },

  onLoad() {
    const app = getApp()
    if (app && app.hydrateAuth) {
      const auth = app.hydrateAuth()
      if (auth && auth.accessToken) {
        wx.switchTab({ url: '/pages/home/home' })
      }
    }
  },

  onAgreementChange(e) {
    this.setData({
      isAgreed: e.detail.value.length > 0
    })
  },

  checkAgreement() {
    if (!this.data.isAgreed) {
      wx.showToast({
        title: '请先阅读并同意服务协议与隐私政策',
        icon: 'none'
      })
      return false
    }
    return true
  },

  onWechatLogin() {
    if (!this.checkAgreement()) return
    if (this.data.loading) return

    this.setData({ loading: true })
    wx.showLoading({ title: '登录中...' })

    wx.login({
      success: (res) => {
        const code = res && res.code
        if (!code) {
          wx.showToast({ title: '获取登录态失败', icon: 'none' })
          return
        }
        post('users/login/', { code }, { needAuth: false })
          .then((loginRes) => {
            if (loginRes && loginRes.access) {
              saveAuth(loginRes)
              const app = getApp()
              if (app && app.hydrateAuth) {
                app.hydrateAuth()
              }
              if (app && app.hasRealOpenId) {
                app.hasRealOpenId()
              }
              wx.showToast({ title: '登录成功', icon: 'success' })
              setTimeout(() => {
                wx.navigateBack({
                  fail: () => {
                    wx.switchTab({ url: '/pages/home/home' })
                  }
                })
              }, 800)
              return
            }
            wx.showToast({ title: '登录失败：返回数据异常', icon: 'none' })
          })
          .catch((err) => {
            wx.showToast({ title: (err && err.message) || '登录失败，请重试', icon: 'none' })
          })
      },
      fail: () => {
        wx.showToast({ title: '微信登录失败', icon: 'none' })
      },
      complete: () => {
        wx.hideLoading()
        this.setData({ loading: false })
      }
    })
  },

  onShowAgreement() {
    wx.showModal({
      title: '用户服务协议',
      content: '登录后可使用课程预约、购卡支付、器械查看、AI问答等服务。系统会在必要范围内使用你的登录信息完成身份识别与业务处理。',
      showCancel: false
    })
  },

  onShowPrivacy() {
    wx.showModal({
      title: '隐私政策',
      content: '系统仅在登录鉴权、订单处理、会员资料展示等业务场景下使用必要信息，不会超出健身服务范围收集或使用你的个人数据。',
      showCancel: false
    })
  }
})
