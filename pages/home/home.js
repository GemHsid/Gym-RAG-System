const { get, post, getApiBaseUrl } = require('../../utils/request')

const BANNER_MAP = {
  brand: '',
  store: '',
  rest: '',
  locker: ''
}

const LOCAL_HOME_ASSETS = {
  brand: '/首页图像/品牌介绍.png',
  store: '/首页图像/门店环境.png',
  rest: '/首页图像/休息区.png',
  locker: '/首页图像/更衣室.png',
  logo: '/首页图像/LOGO.png'
}

Page({
  data: {
    currentBanner: '',
    bannerMap: { ...BANNER_MAP },
    gymLogoSrc: LOCAL_HOME_ASSETS.logo,
    gymInfo: {},
    membershipCards: [],
    recommendedCourses: [],
    recommendedEquipment: [],
    homeStatus: 'loading',
    homeStatusText: '加载中...',
    showRedeemModal: false,
    redeemCode: '',
    showBuyModal: false,
    selectedCard: null,
    productRecommendation: '',
    buyBtnText: '请认真阅读 5s',
    buyBtnDisabled: true,
    isAgreementChecked: false,
    shakeAnimation: false
  },

  getServerBaseUrl() {
    const api = String(getApiBaseUrl() || '').replace(/\/+$/, '')
    return api.replace(/\/api$/i, '')
  },

  normalizeMediaUrl(url) {
    const raw = String(url || '')
    if (!raw) return ''
    if (/^https?:\/\//i.test(raw)) return raw
    if (raw.startsWith('/')) {
      return `${this.getServerBaseUrl()}${raw}`
    }
    return `${this.getServerBaseUrl()}/${raw}`
  },

  onLoad() {
    const app = getApp()
    if (app && app.ensureLogin) {
      app.ensureLogin()
        .then(() => this.loadHomeData())
        .catch(() => this.loadHomeData())
      return
    }
    this.loadHomeData()
  },

  onHide() {
    this.clearModalTimers()
  },

  onUnload() {
    this.clearModalTimers()
  },

  onSwitchBanner(e) {
    const type = e.currentTarget.dataset.type
    const url = this.data.bannerMap[type]
    if (url) {
      this.setData({ currentBanner: url })
    }
  },

  onShowMap() {
    if (this.data.bannerMap.store) {
      this.setData({ currentBanner: this.data.bannerMap.store })
    }
  },

  loadHomeData() {
    this.setData({
      homeStatus: 'loading',
      homeStatusText: '加载中...'
    })

    return Promise.allSettled([
      get('home/info/'),
      get('orders/products/')
    ])
      .then(([homeResult, productResult]) => {
        const hasHomeData = homeResult.status === 'fulfilled' && homeResult.value
        const productPayload = productResult.status === 'fulfilled' ? productResult.value : null
        const productList = Array.isArray(productPayload)
          ? productPayload
          : Array.isArray(productPayload && productPayload.products)
            ? productPayload.products
            : []
        const hasProductData = productResult.status === 'fulfilled' && productList.length > 0

        const homeInfo = hasHomeData ? homeResult.value : {}
        const bannerMap = this.buildBannerMap(homeInfo)
        const membershipCards = hasProductData
          ? productList.map(item => this.mapProductCard(item))
          : []

        const homeStatus = hasHomeData || hasProductData ? 'success' : 'error'
        const failedReason = homeResult.status === 'rejected'
          ? homeResult.reason
          : productResult.status === 'rejected'
            ? productResult.reason
            : null
        const homeStatusText = homeStatus === 'error' ? ((failedReason && failedReason.message) || '加载失败') : ''

        this.setData({
          gymInfo: homeInfo,
          bannerMap,
          currentBanner: this.pickCurrentBanner(bannerMap),
          membershipCards,
          productRecommendation: (productPayload && productPayload.recommendation) || '',
          recommendedCourses: Array.isArray(homeInfo.recent_courses) ? homeInfo.recent_courses : [],
          recommendedEquipment: Array.isArray(homeInfo.recommended_equipment)
            ? homeInfo.recommended_equipment.map((item) => ({
                ...item,
                image: item && item.image ? this.normalizeMediaUrl(item.image) : '',
                gif_url: item && item.gif_url ? this.normalizeMediaUrl(item.gif_url) : '',
                display_image: this.resolveEquipmentMedia(item)
              }))
            : [],
          homeStatus,
          homeStatusText
        })
      })
      .catch(() => {
        this.setData({
          gymInfo: {},
          bannerMap: { ...BANNER_MAP },
          currentBanner: '',
          membershipCards: [],
          recommendedCourses: [],
          recommendedEquipment: [],
          productRecommendation: '',
          homeStatus: 'error',
          homeStatusText: '加载失败'
        })
      })
  },

  buildBannerMap(homeInfo = {}) {
    const source = homeInfo && homeInfo.banner_map ? homeInfo.banner_map : {}
    return {
      brand: LOCAL_HOME_ASSETS.brand || this.normalizeMediaUrl(homeInfo.banner_image || source.brand || ''),
      store: LOCAL_HOME_ASSETS.store || this.normalizeMediaUrl(source.store || ''),
      rest: LOCAL_HOME_ASSETS.rest || this.normalizeMediaUrl(source.rest || ''),
      locker: LOCAL_HOME_ASSETS.locker || this.normalizeMediaUrl(source.locker || '')
    }
  },

  pickCurrentBanner(bannerMap = {}) {
    return bannerMap.brand || bannerMap.store || bannerMap.rest || bannerMap.locker || ''
  },

  resolveEquipmentMedia(item = {}) {
    if (item.image) {
      return item.image
    }
    if (item.gif_url) {
      return item.gif_url
    }
    if (item.miniapp_gif_path) {
      return item.miniapp_gif_path
    }
    return ''
  },

  mapProductCard(item = {}) {
    const daysDuration = Number(item.days_duration) || 0
    const firstTag = Array.isArray(item.tags) && item.tags.length ? item.tags[0] : ''
    return {
      id: item.id || Date.now(),
      name: item.name || '会员卡',
      duration: daysDuration > 0 ? `有效期${daysDuration}天` : '有效期以门店规则为准',
      price: this.formatPrice(item.price),
      originalPrice: this.formatPrice(item.original_price),
      tag: item.is_promotion ? (firstTag || '优惠') : firstTag,
      desc: item.description || ''
    }
  },

  formatPrice(value) {
    if (value === undefined || value === null || value === '') {
      return ''
    }
    const numberValue = Number(value)
    if (Number.isNaN(numberValue)) {
      return String(value)
    }
    return numberValue.toFixed(2)
  },

  onBuyCard(e) {
    const id = e.currentTarget.dataset.id
    const card = this.data.membershipCards.find(item => String(item.id) === String(id)) || this.data.membershipCards[0] || null
    this.setData({
      showBuyModal: true,
      selectedCard: card,
      buyBtnText: '请认真阅读 5s',
      buyBtnDisabled: true,
      isAgreementChecked: false,
      shakeAnimation: false
    })

    this.clearModalTimers()
    let count = 5
    this.countdownTimer = setInterval(() => {
      count -= 1
      if (count > 0) {
        this.setData({ buyBtnText: `请认真阅读 ${count}s` })
      } else {
        clearInterval(this.countdownTimer)
        this.countdownTimer = null
        this.setData({
          buyBtnText: '同意协议并购买',
          buyBtnDisabled: false
        })
      }
    }, 1000)
  },

  onAgreementChange() {
    this.setData({ isAgreementChecked: !this.data.isAgreementChecked })
  },

  closeBuyModal() {
    this.clearModalTimers()
    this.setData({ showBuyModal: false })
  },

  onConfirmPay() {
    if (this.data.buyBtnDisabled) return

    const app = getApp()
    if (app && app.ensureRealOpenId && !app.ensureRealOpenId()) {
      return
    }
    if (!this.data.isAgreementChecked) {
      this.setData({ shakeAnimation: true })
      setTimeout(() => {
        this.setData({ shakeAnimation: false })
      }, 500)
      wx.showToast({ title: '请先勾选协议', icon: 'none' })
      return
    }

    const selectedCard = this.data.selectedCard || {}
    const productId = Number(selectedCard.id)
    if (!productId) {
      wx.showToast({ title: '商品信息异常，请稍后重试', icon: 'none' })
      return
    }

    wx.showLoading({ title: '发起支付中...' })
    this.purchaseCard(productId)
      .then((result) => {
        this.setData({ showBuyModal: false })
        this.promptOrderStatus(result)
      })
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '支付失败，请稍后重试',
          icon: 'none'
        })
      })
      .finally(() => {
        wx.hideLoading()
      })
  },

  purchaseCard(productId) {
    return post('orders/purchase/', { product_id: productId })
      .then((res) => {
        const orderId = res.order_id || null
        
        // 提取微信支付参数
        const { timeStamp, nonceStr, package: pkg, signType, paySign } = res

        return new Promise((resolve, reject) => {
          // 模拟拉起微信支付 (真实环境使用 wx.requestPayment)
          wx.showModal({
            title: '模拟微信支付',
            content: `即将支付：¥${this.data.selectedCard.price}\n\n在真实环境中将拉起微信收银台`,
            confirmText: '支付成功',
            cancelText: '取消支付',
            success: (modalRes) => {
              if (modalRes.confirm) {
                // 模拟支付成功后，后端 notify 接口会被微信调用，这里前端直接返回成功
                wx.showToast({ title: '支付成功', icon: 'success' })
                resolve({ orderId, status: 'paid' })
              } else {
                reject({ message: '用户取消支付' })
              }
            },
            fail: () => reject({ message: '支付拉起失败' })
          })

          /* 真实环境代码
          wx.requestPayment({
            timeStamp,
            nonceStr,
            package: pkg,
            signType,
            paySign,
            success: (payRes) => {
              wx.showToast({ title: '支付成功', icon: 'success' })
              resolve({ orderId, status: 'paid' })
            },
            fail: (err) => {
              reject({ message: err.errMsg === 'requestPayment:fail cancel' ? '用户取消支付' : '支付失败' })
            }
          })
          */
        })
      })
  },

  promptOrderStatus(result = {}) {
    const orderId = result.orderId
    if (!orderId) {
      return
    }
    wx.showModal({
      title: '支付完成',
      content: `订单号：${orderId}\n可进入订单页查看状态与申请退款`,
      cancelText: '稍后查看',
      confirmText: '查看订单',
      success: (modalRes) => {
        if (!modalRes.confirm) {
          return
        }
        wx.navigateTo({
          url: `/pages/order/status/status?orderId=${encodeURIComponent(orderId)}&status=paid`
        })
      }
    })
  },

  clearModalTimers() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer)
      this.countdownTimer = null
    }
  },

  onRedeemCoupon() {
    this.setData({
      showRedeemModal: true,
      redeemCode: ''
    })
  },

  closeRedeemModal() {
    this.setData({
      showRedeemModal: false,
      redeemCode: ''
    })
  },

  onRedeemInput(e) {
    this.setData({ redeemCode: e.detail.value })
  },

  preventBubble() {},

  onScanCode() {
    wx.scanCode({
      success: (res) => {
        wx.showToast({
          title: '扫码成功'
        })
      }
    })
  },

  onGymIntro() {
    wx.showToast({ title: '品牌介绍开发中', icon: 'none' })
  },

  onEquipment() {
    wx.navigateTo({
      url: '/pages/equipment/equipment'
    })
  },

  onCourse() {
    wx.switchTab({
      url: '/pages/course/course'
    })
  },

  onBookCourse(e) {
    const courseId = Number(e.currentTarget.dataset.id)
    if (!courseId) {
      wx.showToast({ title: '课程信息异常', icon: 'none' })
      return
    }
    const app = getApp()
    if (app && app.ensureRealOpenId && !app.ensureRealOpenId()) {
      return
    }
    wx.showLoading({ title: '预约提交中...' })
    post('fitness/bookings/', { course_id: courseId })
      .then(() => {
        wx.showModal({
          title: '预约成功',
          content: '预约已提交，可在课程页查看预约记录',
          showCancel: false
        })
        this.loadHomeData()
      })
      .catch((err) => {
        const msg = (err && err.message) || '预约失败'
        if ((err && err.code) === 400 && /已满|课程已满|名额已满/i.test(msg)) {
          wx.showToast({ title: '名额已满', icon: 'none' })
          return
        }
        wx.showToast({ title: msg, icon: 'none' })
      })
      .finally(() => {
        wx.hideLoading()
      })
  },

  onGymDetail() {
    wx.showToast({ title: '门店详情开发中', icon: 'none' })
  },

  onMoreMembership() {
    wx.navigateTo({
      url: '/pages/buy_card/buy_card'
    })
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
        this.closeRedeemModal()
        this.loadHomeData() // Refresh user data if needed (though home doesn't load profile directly, but it's good practice)
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
  }
})
