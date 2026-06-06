const { get, post } = require('./request')

const WX_PAY_CREATE_ENDPOINT = 'orders/wxpay/create/'
const WX_PAY_VERIFY_ENDPOINT = 'orders/wxpay/verify/'
const REFUND_APPLY_ENDPOINT = 'orders/refund/apply/'
const ORDER_STATUS_ENDPOINT = 'orders/status/'
const REFUND_STATUS_ENDPOINT = 'orders/refund/status/'

function normalizePayParams(payload = {}) {
  const params = payload.pay_params || payload.payment_params || payload
  return {
    timeStamp: String(params.timeStamp || params.timestamp || ''),
    nonceStr: params.nonceStr || params.noncestr || '',
    package: params.package || params.packageValue || '',
    signType: params.signType || params.sign_type || 'RSA',
    paySign: params.paySign || params.pay_sign || ''
  }
}

function createWechatPaymentOrder(productId) {
  return post(WX_PAY_CREATE_ENDPOINT, { product_id: productId }).then((result) => {
    const payParams = normalizePayParams(result || {})
    const orderId = (result && (result.order_id || result.orderId)) || null
    return {
      orderId,
      payParams
    }
  })
}

function requestWechatPay(payParams = {}) {
  return new Promise((resolve, reject) => {
    if (!payParams.timeStamp || !payParams.nonceStr || !payParams.package || !payParams.paySign) {
      reject({ code: 400, message: '支付参数不完整，请检查后端签名返回' })
      return
    }
    wx.requestPayment({
      ...payParams,
      success: (res) => resolve(res),
      fail: (err) => reject(err)
    })
  })
}

function verifyWechatPayment(payload = {}) {
  return post(WX_PAY_VERIFY_ENDPOINT, payload)
}

function applyRefund(payload = {}) {
  return post(REFUND_APPLY_ENDPOINT, payload)
}

function getOrderStatus(orderId) {
  return get(ORDER_STATUS_ENDPOINT, { order_id: orderId })
}

function getRefundStatus(orderId) {
  return get(REFUND_STATUS_ENDPOINT, { order_id: orderId })
}

module.exports = {
  createWechatPaymentOrder,
  requestWechatPay,
  verifyWechatPayment,
  applyRefund,
  getOrderStatus,
  getRefundStatus
}
