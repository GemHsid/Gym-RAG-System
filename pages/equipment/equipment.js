const { get, post, getApiBaseUrl } = require('../../utils/request')
const { EQUIPMENT_LIBRARY } = require('./library')

const DEFAULT_CATEGORIES = [{ key: 'all', name: '全部', partId: null }]
const MAINTENANCE_STATUS = 'maintenance'

function normalizePartName(partName = '') {
  return String(partName || '').trim()
}

Page({
  data: {
    categories: DEFAULT_CATEGORIES,
    currentTab: 0,
    equipmentList: [],
    allEquipment: [],
    pageStatus: 'loading',
    pageStatusText: '器械数据加载中...',
    showModal: false,
    selectedItem: null,
    activeDetailTab: 'gif',
    repairFormVisible: false,
    repairIssue: '',
    submittingRepair: false
  },

  onLoad() {
    this.loadAllEquipment()
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

  mapEquipmentItem(item = {}) {
    const miniappGifPath = item && item.miniapp_gif_path ? String(item.miniapp_gif_path) : ''
    const gifUrl = miniappGifPath || (item && item.gif_url ? this.normalizeMediaUrl(item.gif_url) : '')
    const status = String(item.status || 'idle')
    const showMaintenanceStatus = status === MAINTENANCE_STATUS
    return {
      ...item,
      gif_url: gifUrl,
      cover_image: gifUrl,
      list_media: gifUrl,
      status,
      status_label: showMaintenanceStatus ? '维修中' : '',
      show_maintenance_status: showMaintenanceStatus,
      target_muscles: item.target_muscles || '',
      precautions: item.precautions || '',
      training_focus: item.training_focus || '',
      action_tips: item.action_tips || '',
      miniapp_gif_path: miniappGifPath
    }
  },

  buildCategories(list = []) {
    const seen = {}
    const categories = []
    list.forEach((item) => {
      const partName = normalizePartName(item && item.part_name)
      if (!partName || seen[partName]) {
        return
      }
      seen[partName] = true
      categories.push({
        key: `part-${partName}`,
        name: partName,
        partId: partName
      })
    })
    return DEFAULT_CATEGORIES.concat(categories)
  },

  getFallbackEquipment() {
    return EQUIPMENT_LIBRARY.map((item) => this.mapEquipmentItem(item))
  },

  mergeEquipmentList(remoteList = [], fallbackList = []) {
    const mergedMap = new Map()
    fallbackList.forEach((item) => {
      mergedMap.set(String(item.name), item)
    })
    remoteList.forEach((item) => {
      const key = String(item.name || item.id)
      const base = mergedMap.get(key)
      if (!base) {
        return
      }
      mergedMap.set(key, this.mapEquipmentItem({
        ...base,
        ...item,
        part_id: base.part_id,
        part_name: base.part_name,
        location: item.location || base.location,
        target_muscles: item.target_muscles || base.target_muscles,
        description: item.description || base.description,
        precautions: item.precautions || base.precautions,
        training_focus: item.training_focus || base.training_focus,
        action_tips: item.action_tips || base.action_tips,
        miniapp_gif_path: item.miniapp_gif_path || base.miniapp_gif_path,
        gif_url: item.gif_url || base.gif_url
      }))
    })
    return Array.from(mergedMap.values())
      .filter((item) => !!item.gif_url)
      .sort((a, b) => {
      const partDiff = Number(a.part_id || 0) - Number(b.part_id || 0)
      if (partDiff !== 0) {
        return partDiff
      }
      return String(a.name || '').localeCompare(String(b.name || ''), 'zh-CN')
      })
  },

  onTabChange(e) {
    const index = Number(e.currentTarget.dataset.index) || 0
    this.setData({ currentTab: index })
    this.applyCategoryFilter(index)
  },

  applyCategoryFilter(index = 0) {
    const category = this.data.categories[index] || DEFAULT_CATEGORIES[0]
    const allEquipment = Array.isArray(this.data.allEquipment) ? this.data.allEquipment : []
    const filtered = !category.partId
      ? allEquipment
      : allEquipment.filter((item) => normalizePartName(item.part_name) === normalizePartName(category.partId))
    this.setData({
      equipmentList: filtered,
      pageStatus: filtered.length ? 'success' : 'empty',
      pageStatusText: filtered.length ? '' : '暂无器械数据'
    })
  },

  loadAllEquipment() {
    this.setData({
      pageStatus: 'loading',
      pageStatusText: '器械数据加载中...'
    })

    return get('fitness/equipment/', {}, { needAuth: false })
      .then((list) => {
        const fallbackList = this.getFallbackEquipment()
        const remoteList = Array.isArray(list)
          ? list.map((item) => this.mapEquipmentItem(item))
          : []
        const mapped = this.mergeEquipmentList(remoteList, fallbackList)
        const categories = this.buildCategories(mapped)

        this.setData({
          categories,
          allEquipment: mapped,
          currentTab: 0
        })
        this.applyCategoryFilter(0)
      })
      .catch(() => {
        const mapped = this.getFallbackEquipment()
        const categories = this.buildCategories(mapped)
        this.setData({
          categories,
          allEquipment: mapped,
          currentTab: 0,
          equipmentList: mapped,
          pageStatus: 'success',
          pageStatusText: ''
        })
      })
  },

  onRetry() {
    this.loadAllEquipment()
  },

  onEquipmentTap(e) {
    const item = this.mapEquipmentItem(e.currentTarget.dataset.item || {})
    this.setData({
      selectedItem: item,
      showModal: true,
      activeDetailTab: 'gif',
      repairFormVisible: false,
      repairIssue: '',
      submittingRepair: false
    })
  },

  closeModal() {
    this.setData({
      showModal: false,
      repairFormVisible: false,
      repairIssue: '',
      submittingRepair: false
    })
  },

  preventBubble() {},

  onSwitchDetailTab(e) {
    const tab = e.currentTarget.dataset.tab
    if (!tab || tab === this.data.activeDetailTab) {
      return
    }
    this.setData({ activeDetailTab: tab })
  },

  onVideoExplain() {
    this.setData({ activeDetailTab: 'gif' })
  },

  onTextExplain() {
    this.setData({ activeDetailTab: 'desc' })
  },

  onPrecautions() {
    this.setData({ activeDetailTab: 'notice' })
  },

  onOpenRepairForm() {
    const selectedItem = this.data.selectedItem || {}
    if (!selectedItem.id) {
      wx.showToast({ title: '器械信息异常', icon: 'none' })
      return
    }
    this.setData({
      repairFormVisible: true,
      repairIssue: ''
    })
  },

  onRepairInput(e) {
    this.setData({ repairIssue: e.detail.value })
  },

  onCancelRepair() {
    this.setData({
      repairFormVisible: false,
      repairIssue: ''
    })
  },

  updateEquipmentStatus(equipmentId, status) {
    const normalizedStatus = String(status || 'idle')
    const showMaintenanceStatus = normalizedStatus === MAINTENANCE_STATUS
    const statusLabel = showMaintenanceStatus ? '维修中' : ''
    const nextAllEquipment = (this.data.allEquipment || []).map((item) => {
      if (Number(item.id) !== Number(equipmentId)) {
        return item
      }
      return {
        ...item,
        status: normalizedStatus,
        status_label: statusLabel,
        show_maintenance_status: showMaintenanceStatus
      }
    })
    const nextSelectedItem = this.data.selectedItem && Number(this.data.selectedItem.id) === Number(equipmentId)
      ? {
          ...this.data.selectedItem,
          status: normalizedStatus,
          status_label: statusLabel,
          show_maintenance_status: showMaintenanceStatus
        }
      : this.data.selectedItem
    const category = this.data.categories[this.data.currentTab] || DEFAULT_CATEGORIES[0]
    const nextEquipmentList = !category.partId
      ? nextAllEquipment
      : nextAllEquipment.filter((item) => Number(item.part_id) === Number(category.partId))
    this.setData({
      allEquipment: nextAllEquipment,
      equipmentList: nextEquipmentList,
      selectedItem: nextSelectedItem,
      pageStatus: nextEquipmentList.length ? 'success' : 'empty',
      pageStatusText: nextEquipmentList.length ? '' : '暂无器械数据'
    })
  },

  onSubmitRepair() {
    const selectedItem = this.data.selectedItem || {}
    const issueDescription = String(this.data.repairIssue || '').trim()
    if (!selectedItem.id) {
      wx.showToast({ title: '器械信息异常', icon: 'none' })
      return
    }
    if (!issueDescription) {
      wx.showToast({ title: '请填写故障描述', icon: 'none' })
      return
    }
    if (this.data.submittingRepair) {
      return
    }
    this.setData({ submittingRepair: true })
    wx.showLoading({ title: '提交中...' })
    post('equipment/repair/', {
      equipment_id: selectedItem.id,
      equipment_name: selectedItem.name,
      issue_description: issueDescription
    })
      .then(() => {
        this.updateEquipmentStatus(selectedItem.id, 'maintenance')
        this.setData({
          repairFormVisible: false,
          repairIssue: ''
        })
        wx.showToast({
          title: '报修已提交',
          icon: 'success'
        })
      })
      .catch((err) => {
        wx.showToast({
          title: (err && err.message) || '提交失败',
          icon: 'none'
        })
      })
      .finally(() => {
        wx.hideLoading()
        this.setData({ submittingRepair: false })
      })
  },

  onExit() {
    wx.navigateBack()
  }
})
