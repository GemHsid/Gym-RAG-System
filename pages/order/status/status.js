const { applyRefund, getOrderStatus, getRefundStatus } = require('../../../utils/payment')

function getBadgeType(status = '') {
  if (['paid', 'success', 'pay_success'].includes(status)) return 'success'
  if (['refunding', 'refund_pending', 'refund_processing'].includes(status)) return 'refunding'
  if (['refunded', 'refund_success'].includes(status)) return 'refunded'
  if (['failed', 'pay_failed', 'cancelled', 'closed'].includes(status)) return 'failed'
  return 'pending'
}

function getStatusLabel(status = '') {
  if (['paid', 'success', 'pay_success'].includes(status)) return '已支付'
  if (['refunding', 'refund_pending', 'refund_processing'].includes(status)) return '退款中'
  if (['refunded', 'refund_success'].includes(status)) return '已退款'
  if (['failed', 'pay_failed', 'cancelled', 'closed'].includes(status)) return '已关闭'
  return '处理中'
}

function getStatusDesc(status = '') {
  if (['paid', 'success', 'pay_success'].includes(status)) return '订单已支付成功，可正常使用会员权益。'
  if (['refunding', 'refund_pending', 'refund_processing'].includes(status)) return '退款申请已提交，正在处理中。'
  if (['refunded', 'refund_success'].includes(status)) return '退款已完成，相关权益将同步回收。'
  if (['failed', 'pay_failed', 'cancelled', 'closed'].includes(status)) return '订单已关闭，如有疑问请联系门店客服。'
  return '订单处理中，请稍后刷新查看。'
}

Page({
  data: {
    orderId: '',
    orderInfo: null,
    refundInfo: null,
    statusKey: 'pending',
    statusLabel: '处理中',
    statusDesc: '订单处理中，请稍后刷新查看。',
    statusBadgeType: 'pending',
    pageStatus: 'loading',
    pageStatusText: '订单状态加载中...',
    serverOrderNote: '',
    serverRefundNote: '',
    refreshing: false,
    refunding: false,
    canRefund: false
  },

  onLoad(options = {}) {
    const app = getApp()
    if (app && app.ensureRealOpenId && !app.ensureRealOpenId()) {
      this.setData({
        pageStatus: 'error',
        pageStatusText: '未通过真实OpenID校验，暂无法查询订单'
      })
      return
    }
    const orderId = options.orderId || options.order_id || ''
    const status = options.status || 'pending'
    this.setData({ orderId: String(orderId || '') })
    this.updateStatusUI(status)
    if (!orderId) {
      this.setData({
        pageStatus: 'error',
        pageStatusText: '缺少订单号，请从购买成功页进入'
      })
      return
    }
    this.loadOrderStatus()
  },

  updateStatusUI(status) {
    const badgeType = getBadgeType(status)
    this.setData({
      statusKey: status,
      statusBadgeType: badgeType,
      statusLabel: getStatusLabel(status),
      statusDesc: getStatusDesc(status),
      canRefund: badgeType === 'success'
    })
  },

  parseStatus(orderResult, refundResult) {
    // 优先展示退款状态
    const refundStatus = refundResult && (refundResult.refund_status || refundResult.status)
    if (refundStatus) {
      return String(refundStatus)
    }
    const orderStatus = orderResult && (orderResult.order_status || orderResult.status || orderResult.pay_status)
    return String(orderStatus || this.data.statusKey || 'pending')
  },

  loadOrderStatus() {
    const orderId = this.data.orderId
    if (!orderId) {
      return Promise.resolve()
    }
    this.setData({
      refreshing: true,
      pageStatus: 'loading',
      pageStatusText: '订单状态加载中...'
    })
    return Promise.allSettled([
      getOrderStatus(orderId),
      getRefundStatus(orderId)
    ])
      .then(([orderRes, refundRes]) => {
        const orderResult = orderRes.status === 'fulfilled' ? orderRes.value : null
        const refundResult = refundRes.status === 'fulfilled' ? refundRes.value : null
        const statusKey = this.parseStatus(orderResult, refundResult)
        this.updateStatusUI(statusKey)
        this.setData({
          orderInfo: orderResult,
          refundInfo: refundResult,
          serverOrderNote: (orderResult && orderResult.order_status_note) || '',
          serverRefundNote: (refundResult && refundResult.refund_note) || (orderResult && orderResult.refund_note) || '',
          pageStatus: 'success',
          pageStatusText: ''
        })
      })
      .catch((err) => {
        this.setData({
          pageStatus: 'error',
          pageStatusText: (err && err.message) || '订单状态加载失败',
          serverOrderNote: '',
          serverRefundNote: ''
        })
      })
      .finally(() => {
        this.setData({ refreshing: false })
      })
  },

  onRefresh() {
    this.loadOrderStatus()
  },

  onApplyRefund() {
    if (!this.data.canRefund || this.data.refunding) {
      return
    }
    const orderId = this.data.orderId
    if (!orderId) {
      wx.showToast({ title: '缺少订单号', icon: 'none' })
      return
    }
    this.setData({ refunding: true })
    wx.showLoading({ title: '退款申请中...' })
    applyRefund({
      order_id: orderId,
      reason: '用户主动发起退款'
    })
      .then((refundResult) => {
        const refundId = refundResult && refundResult.refund_id ? refundResult.refund_id : '待生成'
        wx.showModal({
          title: '退款申请已提交',
          content: `退款单号：${refundId}`,
          showCancel: false
        })
      })
      .then(() => this.loadOrderStatus())
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '退款申请失败',
          icon: 'none'
        })
      })
      .finally(() => {
        wx.hideLoading()
        this.setData({ refunding: false })
      })
  }
})
