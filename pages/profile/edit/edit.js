const { request } = require('../../../utils/request')
const { saveAuth } = require('../../../utils/auth')

const PROFILE_SAVE_ENDPOINT = { url: 'users/me/', method: 'PATCH' }

Page({
  data: {
    userInfo: {
      avatar: '/assets/images/default-avatar.png',
      nickName: ''
    },
    saving: false
  },

  onLoad() {
    const draft = wx.getStorageSync('localProfileDraft') || {}
    const app = getApp()
    const globalAuth = app && app.globalData ? app.globalData.auth || {} : {}
    this.setData({
      userInfo: {
        avatar: draft.avatar || this.data.userInfo.avatar,
        nickName: draft.nickName || globalAuth.nickname || this.data.userInfo.nickName
      }
    })
  },

  onChangeAvatar() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath
        this.setData({
          'userInfo.avatar': tempFilePath
        })
      }
    })
  },

  onNameChange(e) {
    this.setData({
      'userInfo.nickName': e.detail.value
    })
  },

  persistLocalProfile() {
    const userInfo = this.data.userInfo || {}
    wx.setStorageSync('localProfileDraft', {
      avatar: userInfo.avatar || '',
      nickName: userInfo.nickName || ''
    })
    saveAuth({ nickname: userInfo.nickName || '' })
  },

  submitProfile(payload) {
    return request({
      url: PROFILE_SAVE_ENDPOINT.url,
      method: PROFILE_SAVE_ENDPOINT.method,
      data: payload
    }).catch((err) => {
      throw err
    })
  },

  onSave() {
    if (this.data.saving) {
      return
    }

    const nickname = (this.data.userInfo.nickName || '').trim()
    const avatar = this.data.userInfo.avatar || ''
    if (!nickname) {
      wx.showToast({ title: '请输入昵称', icon: 'none' })
      return
    }

    const payload = {
      nickname,
      avatar
    }

    this.setData({ saving: true })
    wx.showLoading({ title: '保存中' })
    this.submitProfile(payload)
      .then(() => {
        this.persistLocalProfile()
        wx.showToast({ title: '修改成功', icon: 'success' })
        setTimeout(() => {
          wx.navigateBack()
        }, 700)
      })
      .catch((err) => {
        this.persistLocalProfile()
        wx.showToast({
          title: (err && err.message) || '网络异常，已本地保存',
          icon: 'none'
        })
        setTimeout(() => {
          wx.navigateBack()
        }, 900)
      })
      .finally(() => {
        wx.hideLoading()
        this.setData({ saving: false })
      })
  }
})
