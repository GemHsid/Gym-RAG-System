const { get, post } = require('../../utils/request')

Page({
  data: {
    cards: [],
    pageStatus: 'loading',
    pageStatusText: '会员卡加载中...',
    purchasingId: null,
    recommendation: ''
  },

  onLoad() {
    this.loadProducts()
  },

  normalizeProduct(item = {}) {
    const tags = Array.isArray(item.tags) ? item.tags.filter(Boolean) : []
    const price = item.price !== undefined && item.price !== null ? String(item.price) : '0'
    const days = item.days_duration !== undefined ? Number(item.days_duration) : 0
    return {
      id: item.id,
      name: item.name || '会员卡',
      days,
      price,
      desc: item.is_promotion ? '限时优惠' : '单店使用',
      tag: tags[0] || (item.is_promotion ? '促销' : '单店使用')
    }
  },

  loadProducts() {
    this.setData({
      pageStatus: 'loading',
      pageStatusText: '会员卡加载中...'
    })

    return get('orders/products/')
      .then((payload) => {
        const list = Array.isArray(payload)
          ? payload
          : Array.isArray(payload && payload.products)
            ? payload.products
            : []
        const cards = list
          .map(item => this.normalizeProduct(item))
          .filter(item => item.id !== undefined && item.id !== null)
        this.setData({
          recommendation: (payload && payload.recommendation) || '',
          cards,
          pageStatus: cards.length ? 'success' : 'empty',
          pageStatusText: cards.length ? '' : '暂无会员卡产品'
        })
      })
      .catch((err) => {
        this.setData({
          recommendation: '',
          cards: [],
          pageStatus: 'error',
          pageStatusText: (err && err.message) || '加载失败'
        })
      })
  },

  onPurchase(e) {
    const productId = Number(e.currentTarget.dataset.id)
    if (!productId || this.data.purchasingId) {
      return
    }
    const app = getApp()
    if (app && app.ensureRealOpenId && !app.ensureRealOpenId()) {
      return
    }

    this.setData({ purchasingId: productId })
    wx.showLoading({ title: '提交中...' })

    this.purchaseWithBalance(productId)
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '购买失败，请稍后重试',
          icon: 'none'
        })
      })
      .finally(() => {
        wx.hideLoading()
        this.setData({ purchasingId: null })
      })

  },

  purchaseWithBalance(productId) {
    return post('orders/purchase/', { product_id: productId })
      .then((res) => {
        // 根据后端对接.md，成功返回 { new_balance, new_expiry, order_id }
        const orderId = res.order_id || null
        return this.showPurchaseSuccess({
          message: '支付成功，会员权益已生效',
          orderId: orderId
        })
      })
  },

  showPurchaseSuccess({ message = '购买成功', orderId = null }) {
    const orderLine = orderId ? `\n订单号：${orderId}` : ''
    return new Promise((resolve) => {
      wx.showModal({
        title: '购买成功',
        content: `${message}${orderLine}${orderId ? '\n可进入订单页跟踪支付与退款状态' : ''}`,
        cancelText: '完成',
        confirmText: '查看订单',
        success: (modalRes) => {
          if (!modalRes.confirm) {
            resolve()
            return
          }
          if (!orderId) {
            wx.showToast({
              title: '订单号未返回，暂不可查看',
              icon: 'none'
            })
            resolve()
            return
          }
          this.openOrderStatus(orderId, 'paid')
          resolve()
        },
        fail: () => resolve()
      })
    })
  },

  openOrderStatus(orderId, status = 'paid') {
    wx.navigateTo({
      url: `/pages/order/status/status?orderId=${encodeURIComponent(orderId)}&status=${encodeURIComponent(status)}`
    })
  }
})
