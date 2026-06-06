const { get, post, getApiBaseUrl } = require('../../utils/request')
const { getAuthState } = require('../../utils/auth')

const FACE_REGISTER_ENDPOINT = 'users/face/register/'
const FACE_VERIFY_ENDPOINT = 'users/face/verify/'

function getLocalProfileDraft() {
  const draft = wx.getStorageSync('localProfileDraft') || {}
  return {
    avatar: draft.avatar || '',
    nickName: draft.nickName || ''
  }
}

function parseUploadResponse(raw) {
  const payload = typeof raw === 'string' ? JSON.parse(raw || '{}') : (raw || {})
  if (payload.code !== 0) {
    throw new Error(payload.message || '请求失败')
  }
  return payload.data
}

function normalizeMediaUrl(url) {
  if (!url) return ''
  if (/^https?:\/\//.test(url)) return url
  const baseUrl = getApiBaseUrl()
  const root = baseUrl.replace(/\/+$/, '').replace(/\/api\/?$/, '')
  return `${root}${url.startsWith('/') ? '' : '/'}${url}`
}

Page({
  data: {
    isLoggedIn: false,
    userInfo: {
      id: '',
      avatar: '/assets/images/default-avatar.png',
      nickName: '',
      phone: '',
      balance: ''
    },
    memberCard: {
      cardName: '会员卡',
      daysRemaining: 0,
      statusText: '',
      expiryText: ''
    },
    stats: {
      trainingDays: 0,
      trainingCount: 0,
      monthlyCount: 0,
      monthlyDuration: 0
    },
    showGuide: false,
    showRepair: false,
    showHistory: false,
    showFeedback: false,
    showRedeemModal: false,
    showFaceVerify: false,
    redeemCode: '',
    historyList: [],
    profileNotes: {
      memberBenefits: '',
      faceNotice: '',
      doorNotice: '',
      visitNotice: '',
      groupBuyNotice: '',
      entryGuideText: ''
    },
    feedbackExamples: [],
    profileStatus: 'loading',
    profileStatusText: '加载中...',
    faceImageUrl: '',
    faceVerifyStatusText: '未录入',
    repairEquipmentName: '',
    repairDescription: '',
    feedbackContent: '',
    feedbackContact: '',
    guideVideoUrl: '',
    guideCoverImage: '',
    submittingRepair: false,
    submittingFeedback: false,
    submittingFace: false,
    submittingDoor: false
  },

  onLoad() {
    this.loadProfileData()
  },

  onShow() {
    this.loadProfileData()
  },

  loadProfileData() {
    const authState = getAuthState()
    const isLoggedIn = !!authState.accessToken

    if (!isLoggedIn) {
      this.setData({
        isLoggedIn: false,
        userInfo: {
          avatar: '/assets/images/default-avatar.png',
          nickName: '',
          phone: '',
          id: '',
          balance: ''
        },
        memberCard: { cardName: '会员卡', daysRemaining: 0, statusText: '未登录', expiryText: '请先登录' },
        stats: { trainingDays: 0, trainingCount: 0, monthlyCount: 0, monthlyDuration: 0 },
        historyList: [],
        profileNotes: {
          memberBenefits: '',
          faceNotice: '',
          doorNotice: '',
          visitNotice: '',
          groupBuyNotice: '',
          entryGuideText: ''
        },
        feedbackExamples: [],
        faceImageUrl: '',
        faceVerifyStatusText: '未录入',
        profileStatus: 'success',
        profileStatusText: ''
      })
      return
    }

    this.setData({
      isLoggedIn: true,
      profileStatus: 'loading',
      profileStatusText: '加载中...'
    })

    return Promise.allSettled([
      get('users/profile/'),
      get('users/visit-history/')
    ])
      .then(([profileResult, historyResult]) => {
        const authState = getAuthState()
        const localDraft = getLocalProfileDraft()
        const profile = profileResult.status === 'fulfilled' ? profileResult.value : null
        const history = historyResult.status === 'fulfilled' ? historyResult.value : null
        const hasProfile = !!profile
        const hasHistory = Array.isArray(history)

        const userInfo = {
          id: profile && profile.id ? profile.id : '',
          avatar: profile && profile.avatar ? profile.avatar : (localDraft.avatar || '/assets/images/default-avatar.png'),
          nickName: profile && profile.nickname ? profile.nickname : (localDraft.nickName || authState.nickname || ''),
          phone: profile && profile.phone ? profile.phone : '',
          balance: profile && profile.balance !== undefined ? profile.balance : ''
        }

        const membershipExpiry = profile && profile.membership_expiry ? String(profile.membership_expiry) : ''
        const membershipStatus = profile && profile.membership_status ? String(profile.membership_status) : 'none'
        const statusText = membershipStatus === 'active' ? '生效中' : membershipStatus === 'expired' ? '已到期' : '未开通'

        const memberCard = {
          cardName: '会员卡',
          daysRemaining: profile && profile.days_remaining !== undefined ? profile.days_remaining : 0,
          statusText,
          expiryText: membershipExpiry ? `有效期至 ${membershipExpiry}` : ''
        }

        const stats = {
          trainingDays: profile && profile.total_training_days !== undefined ? profile.total_training_days : 0,
          trainingCount: profile && profile.total_training_count !== undefined ? profile.total_training_count : 0,
          monthlyCount: profile && profile.monthly_stats && profile.monthly_stats.count !== undefined ? profile.monthly_stats.count : 0,
          monthlyDuration: profile && profile.monthly_stats && profile.monthly_stats.duration !== undefined ? profile.monthly_stats.duration : 0
        }

        const historyList = hasHistory && history.length
          ? history.map(item => ({
              id: item.id || Date.now(),
              date: item.visit_time || item.date || '',
              method: item.method || '人脸识别'
            }))
          : []
        const profileNotes = {
          memberBenefits: (profile && profile.member_benefits) || '',
          faceNotice: (profile && profile.face_notice) || '',
          doorNotice: (profile && profile.door_notice) || '',
          visitNotice: (profile && profile.visit_notice) || '',
          groupBuyNotice: (profile && profile.group_buy_notice) || '',
          entryGuideText: (profile && profile.entry_guide_text) || ''
        }
        const feedbackExamples = Array.isArray(profile && profile.feedback_examples) ? profile.feedback_examples : []
        const faceImageUrl = normalizeMediaUrl(profile && profile.face_image ? profile.face_image : '')

        const profileStatus = hasProfile || hasHistory ? 'success' : 'error'
        const failedReason = profileResult.status === 'rejected'
          ? profileResult.reason
          : historyResult.status === 'rejected'
            ? historyResult.reason
            : null
        const profileStatusText = profileStatus === 'error' ? (((failedReason && failedReason.message) || '加载失败')) : ''

        this.setData({
          userInfo,
          memberCard,
          stats,
          historyList,
          profileNotes,
          feedbackExamples,
          faceImageUrl,
          faceVerifyStatusText: faceImageUrl ? '已录入，可重新拍照' : '未录入',
          profileStatus,
          profileStatusText
        })
      })
      .catch(() => {
        const localDraft = getLocalProfileDraft()
        const authState = getAuthState()
        this.setData({
          userInfo: {
            id: '',
            avatar: localDraft.avatar || '/assets/images/default-avatar.png',
            nickName: localDraft.nickName || authState.nickname || '',
            phone: '',
            balance: ''
          },
          memberCard: { cardName: '会员卡', daysRemaining: 0, statusText: '', expiryText: '' },
          stats: { trainingDays: 0, trainingCount: 0, monthlyCount: 0, monthlyDuration: 0 },
          historyList: [],
          profileNotes: {
            memberBenefits: '',
            faceNotice: '',
            doorNotice: '',
            visitNotice: '',
            groupBuyNotice: '',
            entryGuideText: ''
          },
          feedbackExamples: [],
          faceImageUrl: this.data.faceImageUrl || '',
          faceVerifyStatusText: this.data.faceImageUrl ? '已录入，可重新拍照' : '未录入',
          profileStatus: 'error',
          profileStatusText: '加载失败'
        })
      })
  },

  onHeaderClick() {
    if (this.data.isLoggedIn) {
      wx.navigateTo({ url: '/pages/profile/edit/edit' })
    } else {
      wx.navigateTo({ url: '/pages/login/login' })
    }
  },

  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          const { clearAuth } = require('../../utils/auth')
          clearAuth()
          this.loadProfileData()
          wx.showToast({ title: '已退出登录', icon: 'success' })
        }
      }
    })
  },

  onBuyCard() {
    if (!this.data.isLoggedIn) return wx.navigateTo({ url: '/pages/login/login' })
    wx.navigateTo({
      url: '/pages/buy_card/buy_card'
    })
  },

  onRedeem() {
    if (!this.data.isLoggedIn) return wx.navigateTo({ url: '/pages/login/login' })
    this.setData({ showRedeemModal: true })
  },

  onChat() {
    if (!this.data.isLoggedIn) return wx.navigateTo({ url: '/pages/login/login' })
    wx.switchTab({
      url: '/pages/ai/ai'
    })
  },

  onFaceVerify() {
    if (!this.data.isLoggedIn) return wx.navigateTo({ url: '/pages/login/login' })
    this.setData({
      showFaceVerify: true,
      faceVerifyStatusText: this.data.faceImageUrl ? '已录入，可重新拍照' : '未录入'
    })
  },

  onGuide() {
    wx.showLoading({ title: '加载中...' })
    get('gym/guide/')
      .then((res) => {
        if (!res.video_url) {
          throw new Error('暂无视频指南')
        }
        this.setData({
          showGuide: true,
          guideVideoUrl: res.video_url,
          guideCoverImage: res.cover_image || ''
        })
      })
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '加载指南失败',
          icon: 'none'
        })
      })
      .finally(() => {
        wx.hideLoading()
      })
  },

  onRepair() {
    this.setData({
      showRepair: true,
      repairEquipmentName: '',
      repairDescription: ''
    })
  },

  onHistory() {
    if (!this.data.isLoggedIn) return wx.navigateTo({ url: '/pages/login/login' })
    this.setData({ showHistory: true })
  },

  onFeedback() {
    this.setData({
      showFeedback: true,
      feedbackContent: '',
      feedbackContact: ''
    })
  },

  closeModal() {
    this.setData({
      showGuide: false,
      showRepair: false,
      showHistory: false,
      showFeedback: false,
      showRedeemModal: false,
      showFaceVerify: false
    })
  },

  preventBubble() {},

  onScanRedeem() {
    wx.scanCode({
      success: (res) => { 
        this.setData({ redeemCode: res.result || '' })
        wx.showToast({ title: '扫码成功' }) 
      }
    })
  },

  onRedeemInput(e) {
    this.setData({ redeemCode: e.detail.value })
  },

  confirmRedeem() {
    const redeemCode = (this.data.redeemCode || '').trim()
    if (!redeemCode) {
      wx.showToast({ title: '请输入券码', icon: 'none' })
      return
    }

    wx.showLoading({ title: '核销中...' })
    post('orders/redeem/', {
      platform: 'meituan',
      coupon_code: redeemCode
    })
      .then((res) => {
        wx.showModal({
          title: '核销成功',
          content: `获得：${res.product_name || '单次体验卡'}\n有效期至：${res.valid_until || ''}`,
          showCancel: false
        })
        this.closeModal()
        this.loadProfileData() // 刷新个人信息（更新剩余天数等）
      })
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '核销失败，请稍后重试',
          icon: 'none'
        })
      })
      .finally(() => {
        wx.hideLoading()
      })
  },

  onRepairEquipmentInput(e) {
    this.setData({ repairEquipmentName: e.detail.value })
  },

  onRepairDescriptionInput(e) {
    this.setData({ repairDescription: e.detail.value })
  },

  onFeedbackContentInput(e) {
    this.setData({ feedbackContent: e.detail.value })
  },

  onFeedbackContactInput(e) {
    this.setData({ feedbackContact: e.detail.value })
  },

  chooseFaceFile() {
    return new Promise((resolve, reject) => {
      if (wx.chooseMedia) {
        wx.chooseMedia({
          count: 1,
          mediaType: ['image'],
          sourceType: ['camera'],
          success: (res) => {
            const file = res && res.tempFiles && res.tempFiles[0]
            if (!file || !file.tempFilePath) {
              reject({ message: '未获取到有效照片，请重试' })
              return
            }
            resolve(file.tempFilePath)
          },
          fail: reject
        })
        return
      }
      wx.chooseImage({
        count: 1,
        sourceType: ['camera'],
        success: (res) => {
          const path = res && res.tempFilePaths && res.tempFilePaths[0]
          if (!path) {
            reject({ message: '未获取到有效照片，请重试' })
            return
          }
          resolve(path)
        },
        fail: reject
      })
    })
  },

  uploadFaceFile(filePath, endpoint, extraData = {}) {
    const baseUrl = getApiBaseUrl()
    const uploadUrl = `${baseUrl}/${endpoint}`.replace(/([^:]\/)\/+/g, '$1')
    return new Promise((resolve, reject) => {
      wx.uploadFile({
        url: uploadUrl,
        filePath,
        name: 'face_image',
        formData: extraData,
        header: {
          Authorization: `Bearer ${(getApp().globalData.auth && getApp().globalData.auth.accessToken) || ''}`
        },
        success: (res) => {
          try {
            resolve(parseUploadResponse(res.data))
          } catch (error) {
            reject({ message: error.message || '上传结果解析失败' })
          }
        },
        fail: (err) => {
          const errMsg = (err && err.errMsg) || ''
          if (/not in domain list/i.test(errMsg)) {
            reject({ message: '上传失败：域名未加入合法域名白名单' })
            return
          }
          reject({ message: errMsg ? `上传失败：${errMsg}` : '上传失败，请稍后重试' })
        }
      })
    }).catch((err) => {
      const message = (err && err.message) || ''
      if (/404|not found|不存在/i.test(message)) {
        return Promise.reject({ message: '人脸接口未配置，请联系后端接入' })
      }
      throw err
    })
  },

  onCaptureFace() {
    if (this.data.submittingFace) {
      return
    }
    this.setData({ submittingFace: true })
    wx.showLoading({ title: '处理中...' })
    this.chooseFaceFile()
      .then(filePath => this.uploadFaceFile(filePath, FACE_REGISTER_ENDPOINT))
      .then((userProfile) => {
        const imageUrl = normalizeMediaUrl(userProfile && userProfile.face_image ? userProfile.face_image : '')
        this.setData({
          faceImageUrl: imageUrl,
          faceVerifyStatusText: '已录入，可重新拍照'
        })
        wx.showToast({
          title: '人脸录入成功',
          icon: 'success'
        })
      })
      .catch((err) => {
        const message = (err && err.message) || ''
        if (/auth deny|authorize|permission/i.test(message)) {
          wx.showModal({
            title: '相机权限未开启',
            content: '请在微信设置中开启相机权限后重试',
            showCancel: false
          })
          return
        }
        wx.showToast({
          title: message || '人脸录入失败，请稍后重试',
          icon: 'none'
        })
      })
      .finally(() => {
        wx.hideLoading()
        this.setData({ submittingFace: false })
      })
  },

  onDoorAccess() {
    if (this.data.submittingDoor) {
      return
    }
    if (!this.data.faceImageUrl) {
      wx.showToast({ title: '请先完成人脸录入', icon: 'none' })
      return
    }
    this.setData({ submittingDoor: true })
    wx.showLoading({ title: '门禁验证中...' })
    this.chooseFaceFile()
      .then(filePath => this.uploadFaceFile(filePath, FACE_VERIFY_ENDPOINT, { device_id: 'MINI_PROGRAM_DOOR_01' }))
      .then((result) => {
        const passed = !!(result && result.passed)
        const similarity = result && result.similarity !== undefined ? Number(result.similarity) : 0
        const action = result && result.action ? String(result.action) : 'none'
        const actionText = action === 'checkin' ? '入场成功' : action === 'checkout' ? '离场成功' : passed ? '验证通过' : '验证失败'
        wx.showModal({
          title: passed ? '门禁通过' : '门禁拒绝',
          content: `${actionText}\n相似度：${Number.isFinite(similarity) ? similarity.toFixed(1) : '0.0'}`,
          showCancel: false
        })
        return get('users/visit-history/').then((history) => {
          if (Array.isArray(history) && history.length) {
            this.setData({
              historyList: history.map(item => ({
                id: item.id || Date.now(),
                date: item.visit_time || item.date || '',
                method: item.method || '人脸识别'
              }))
            })
          }
        }).catch(() => null)
      })
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '门禁验证失败，请稍后重试',
          icon: 'none'
        })
      })
      .finally(() => {
        wx.hideLoading()
        this.setData({ submittingDoor: false })
      })
  },

  submitRepair() {
    const equipmentName = (this.data.repairEquipmentName || '').trim()
    const issueDescription = (this.data.repairDescription || '').trim()
    if (!issueDescription) {
      wx.showToast({
        title: '请先填写故障描述',
        icon: 'none'
      })
      return
    }
    if (this.data.submittingRepair) {
      return
    }

    this.setData({ submittingRepair: true })

    post('equipment/repair/', {
      equipment_name: equipmentName || '未指定器械',
      issue_description: issueDescription
    })
      .then((result) => {
        const repairId = result && result.repair_id ? `，单号 #${result.repair_id}` : ''
        wx.showToast({
          title: `报修成功${repairId}`,
          icon: 'none'
        })
        this.closeModal()
      })
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '报修失败，请稍后重试',
          icon: 'none'
        })
      })
      .finally(() => {
        this.setData({ submittingRepair: false })
      })
  },

  submitFeedback() {
    const content = (this.data.feedbackContent || '').trim()
    const contact = (this.data.feedbackContact || '').trim()
    if (!content) {
      wx.showToast({
        title: '请先填写留言内容',
        icon: 'none'
      })
      return
    }
    if (this.data.submittingFeedback) {
      return
    }

    this.setData({ submittingFeedback: true })

    post('users/feedback/', {
      content,
      contact: contact || undefined
    })
      .then(() => {
        wx.showToast({
          title: '留言提交成功',
          icon: 'success'
        })
        this.closeModal()
      })
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '提交失败，请稍后重试',
          icon: 'none'
        })
      })
      .finally(() => {
        this.setData({ submittingFeedback: false })
      })
  }
})
