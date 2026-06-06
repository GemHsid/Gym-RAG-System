const { get, getApiBaseUrl } = require('../../utils/request')

Page({
  data: {
    selectedDateIndex: 0,
    showFilter: false,
    selectedFilter: '全部课程',
    filterOptions: ['全部课程'],
    dates: [],
    coaches: [],
    allCoaches: [],
    courseCategories: [],
    courseCategoriesText: '',
    membershipTip: '',
    listStatus: 'loading',
    listStatusText: '加载中...'
  },

  onLoad() {
    const dates = this.buildDates()
    this.setData({ dates })
    this.loadCourseData(0)
  },

  buildDates() {
    const weekLabels = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    const today = new Date()
    return Array.from({ length: 7 }).map((_, index) => {
      const date = new Date(today)
      date.setDate(today.getDate() + index)
      return {
        date: String(date.getDate()),
        week: index === 0 ? '今日' : weekLabels[date.getDay()],
        fullDate: this.formatDate(date)
      }
    })
  },

  formatDate(date) {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
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

  loadCourseData(dateIndex) {
    return this.loadCourseDataWithFallback(dateIndex, true)
  },

  loadCourseDataWithFallback(dateIndex, allowFallback) {
    const selected = this.data.dates[dateIndex]
    if (!selected) {
      return Promise.resolve()
    }
    this.setData({
      selectedDateIndex: dateIndex,
      listStatus: 'loading',
      listStatusText: '加载中...'
    })

    return get('courses/schedule/', { date: selected.fullDate }, { needAuth: false })
      .then((payload) => {
        const slots = payload && payload.time_slots ? payload.time_slots : {}
        const list = []
        ;['morning', 'afternoon', 'evening'].forEach((key) => {
          const items = Array.isArray(slots[key]) ? slots[key] : []
          items.forEach((c) => list.push(c))
        })
        const allCoaches = this.groupCoursesByCoach(list)
        const filterOptions = this.collectFilterOptions(allCoaches)
        const nextFilter = filterOptions.includes(this.data.selectedFilter) ? this.data.selectedFilter : '全部课程'
        const coaches = this.applyCoachFilter(allCoaches, nextFilter)

        if (allowFallback && !allCoaches.length) {
          const nextDateIndex = this.findNextAvailableDateIndex(dateIndex)
          if (nextDateIndex !== -1 && nextDateIndex !== dateIndex) {
            return this.loadCourseDataWithFallback(nextDateIndex, false)
          }
        }

        this.setData({
          allCoaches,
          coaches,
          selectedFilter: nextFilter,
          courseCategories: Array.isArray(payload && payload.course_categories) ? payload.course_categories : [],
          courseCategoriesText: Array.isArray(payload && payload.course_categories) ? payload.course_categories.join(' / ') : '',
          membershipTip: (payload && payload.membership_tip) || '',
          filterOptions,
          listStatus: 'success',
          listStatusText: ''
        })
      })
      .catch((err) => {
        this.setData({
          allCoaches: [],
          coaches: [],
          courseCategories: [],
          courseCategoriesText: '',
          membershipTip: '',
          filterOptions: ['全部课程'],
          listStatus: 'error',
          listStatusText: (err && err.message) || '加载失败'
        })
      })
  },

  findNextAvailableDateIndex(currentIndex) {
    const total = Array.isArray(this.data.dates) ? this.data.dates.length : 0
    for (let index = currentIndex + 1; index < total; index += 1) {
      return index
    }
    return -1
  },

  groupCoursesByCoach(courses = []) {
    const map = new Map()
    courses.forEach((c) => {
      const coachName = (c && c.coach_name) || '未分配教练'
      const coachTitle = (c && c.coach_title) || ''
      const defaultAvatar = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(coachName.charAt(0)) + '&background=random&color=fff&size=128'
      const coachAvatar = this.normalizeMediaUrl(c && c.coach_avatar) || defaultAvatar
      const coachKey = `${coachName}__${coachTitle}__${coachAvatar}`
      if (!map.has(coachKey)) {
        map.set(coachKey, {
          id: coachKey,
          name: coachName,
          title: coachTitle,
          avatar: coachAvatar,
          action: '全部课程',
          actionType: 'list',
          isExpanded: false,
          courses: []
        })
      }
      const coach = map.get(coachKey)
      coach.courses.push({
        id: c.id,
        name: `${c.start_time} ${c.name}`,
        avatar: coachAvatar,
        category: c.category || '',
        intensity: c.intensity_level || '',
        suitableFor: c.suitable_for || ''
      })
    })
    return Array.from(map.values())
  },

  collectFilterOptions(coaches) {
    const set = new Set(['全部课程'])
    coaches.forEach((coach) => {
      if (Array.isArray(coach.courses)) {
        coach.courses.forEach((course) => {
          const rawName = course && course.name ? String(course.name).replace(/^\d{2}:\d{2}\s+/, '') : ''
          if (rawName) {
            set.add(rawName)
          }
        })
      }
    })
    const options = Array.from(set)
    return options.length ? options : ['全部课程']
  },

  applyCoachFilter(coaches, selectedFilter) {
    if (selectedFilter === '全部课程') {
      return coaches.map(item => ({ ...item }))
    }
    return coaches
      .filter((coach) => {
        if (!Array.isArray(coach.courses)) {
          return false
        }
        return coach.courses.some(course => String(course.name || '').replace(/^\d{2}:\d{2}\s+/, '') === selectedFilter)
      })
      .map((coach) => ({
        ...coach,
        courses: coach.courses.filter(course => String(course.name || '').replace(/^\d{2}:\d{2}\s+/, '') === selectedFilter)
      }))
  },

  onSelectDate(e) {
    const index = Number(e.currentTarget.dataset.index) || 0
    this.loadCourseData(index)
  },

  onToggleFilter() {
    this.setData({ showFilter: !this.data.showFilter })
  },

  onSelectFilter(e) {
    const selectedFilter = e.currentTarget.dataset.val
    const coaches = this.applyCoachFilter(this.data.allCoaches, selectedFilter)
    this.setData({
      selectedFilter,
      coaches,
      showFilter: false
    })
  },

  onCoachAction(e) {
    const id = e.currentTarget.dataset.id
    const allCoaches = this.data.allCoaches.map(item => ({ ...item, courses: item.courses ? [...item.courses] : [] }))
    const coach = allCoaches.find(item => item.id === id)
    if (!coach) {
      return
    }
    if (coach.actionType !== 'list' || !coach.courses || !coach.courses.length) {
      this.onBooking(e)
      return
    }
    const updatedAllCoaches = allCoaches.map(item => {
      if (item.id !== id) {
        return item
      }
      const isExpanded = !item.isExpanded
      return {
        ...item,
        isExpanded,
        action: isExpanded ? '收起' : '全部授课'
      }
    })
    const coaches = this.applyCoachFilter(updatedAllCoaches, this.data.selectedFilter)
    this.setData({
      allCoaches: updatedAllCoaches,
      coaches
    })
  },

  onBooking(e) {
    wx.navigateTo({
      url: '/pages/course/detail?id=' + e.currentTarget.dataset.id
    })
  }
})
