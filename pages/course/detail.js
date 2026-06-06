const { get, post } = require('../../utils/request')

Page({
  data: {
    courseId: null,
    reserving: false,
    pageStatus: 'loading',
    pageStatusText: '加载中...',
    course: null,
    canReserve: false,
    reserveButtonText: '提交预约',
    reserveDisabledReason: ''
  },

  onLoad(options = {}) {
    const parsedId = Number(options.id)
    this.setData({
      courseId: Number.isNaN(parsedId) ? options.id : parsedId
    })
    this.loadCourse()
  },

  loadCourse() {
    const courseId = Number(this.data.courseId)
    if (!courseId) {
      this.setData({
        pageStatus: 'error',
        pageStatusText: '课程ID无效',
        course: null
      })
      return Promise.resolve()
    }
    this.setData({
      pageStatus: 'loading',
      pageStatusText: '加载中...',
      course: null
    })
    return get(`fitness/courses/${courseId}/`, {}, { needAuth: false })
      .then((course) => {
        if (course.start_time) {
          const d = new Date(course.start_time)
          if (!isNaN(d.getTime())) {
            const year = d.getFullYear()
            const month = String(d.getMonth() + 1).padStart(2, '0')
            const day = String(d.getDate()).padStart(2, '0')
            const hours = String(d.getHours()).padStart(2, '0')
            const minutes = String(d.getMinutes()).padStart(2, '0')
            course.formatted_time = `${year}-${month}-${day} ${hours}:${minutes}`
          } else {
            course.formatted_time = course.start_time
          }
        }
        const reserveState = this.getReserveState(course)
        this.setData({
          course,
          canReserve: reserveState.canReserve,
          reserveButtonText: reserveState.buttonText,
          reserveDisabledReason: reserveState.reason,
          pageStatus: 'success',
          pageStatusText: ''
        })
      })
      .catch((err) => {
        this.setData({
          course: null,
          canReserve: false,
          reserveButtonText: '提交预约',
          reserveDisabledReason: '',
          pageStatus: 'error',
          pageStatusText: (err && err.message) || '加载失败'
        })
      })
  },

  getReserveState(course = {}) {
    const availableSeatsRaw = course.available_seats
    const availableSeats = availableSeatsRaw !== undefined
      ? Number(availableSeatsRaw)
      : Number(course.capacity || 0) - Number(course.booked_count || 0)
    const hasSeats = Number.isFinite(availableSeats) ? availableSeats > 0 : true
    const startTime = course.start_time ? new Date(course.start_time) : null
    const hasStarted = !!(startTime && !isNaN(startTime.getTime()) && startTime.getTime() <= Date.now())

    if (hasStarted) {
      return {
        canReserve: false,
        buttonText: '课程已开始',
        reason: '当前课程已开始或已结束'
      }
    }
    if (!hasSeats) {
      return {
        canReserve: false,
        buttonText: '名额已满',
        reason: '当前课程名额已满'
      }
    }
    return {
      canReserve: true,
      buttonText: '提交预约',
      reason: ''
    }
  },

  onBack() {
    wx.navigateBack()
  },

  onReserve() {
    if (this.data.reserving) {
      return
    }
    if (!this.data.canReserve) {
      wx.showToast({
        title: this.data.reserveDisabledReason || '当前课程暂不可预约',
        icon: 'none'
      })
      return
    }
    const app = getApp()
    if (app && app.ensureRealOpenId && !app.ensureRealOpenId()) {
      return
    }

    const courseId = Number(this.data.courseId)
    if (!courseId) {
      wx.showToast({
        title: '课程ID无效，请返回重试',
        icon: 'none'
      })
      return
    }
    const payload = { course_id: courseId }

    this.setData({ reserving: true })
    wx.showLoading({ title: '预约提交中...' })

    post('fitness/bookings/', payload)
      .then(() => {
        wx.showModal({
          title: '预约成功',
          content: '预约已提交',
          showCancel: false
        })
        this.loadCourse()
      })
      .catch((err) => {
        const msg = (err && err.message) || '预约失败，请稍后重试'
        if ((err && err.code) === 400 && /已满|课程已满|名额已满/i.test(msg)) {
          wx.showToast({ title: '名额已满', icon: 'none' })
          return
        }
        if ((err && err.code) === 400 && /已开始|已结束/i.test(msg)) {
          this.setData({
            canReserve: false,
            reserveButtonText: '课程已开始',
            reserveDisabledReason: '当前课程已开始或已结束'
          })
          wx.showToast({ title: '课程已开始', icon: 'none' })
          return
        }
        if ((err && err.code) === 400 && /已预约/i.test(msg)) {
          this.setData({
            canReserve: false,
            reserveButtonText: '已预约',
            reserveDisabledReason: '你已预约该课程'
          })
          wx.showToast({ title: '你已预约该课程', icon: 'none' })
          return
        }
        wx.showToast({ title: msg, icon: 'none' })
      })
      .finally(() => {
        wx.hideLoading()
        this.setData({ reserving: false })
      })
  },

  onBuyCard() {
    wx.navigateTo({
      url: '/pages/buy_card/buy_card'
    })
  }
})
