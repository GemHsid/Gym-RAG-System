const { get, post } = require('../../utils/request')
const { EQUIPMENT_LIBRARY } = require('../equipment/library')

const DIRECT_RAG_BASE_URL = 'https://4251qg6o45kfqvzy.apps.gitee-ai.com:32481'
const DIRECT_VLLM_BASE_URL = 'https://4251qg6o45kfqvzy.apps.gitee-ai.com:32481'
const DIRECT_VLLM_MODEL = '/mnt/moark-models/Qwen3-4B'
const RAG_ENDPOINT_CANDIDATES = [
  '/v1/chat/completions',
  '/chat',
  '/chat/',
  '/query',
  '/query/',
  '/query/stream',
  '/query/stream/',
  '/rag/search',
  '/rag/search/',
  ''
]

function joinEndpoint(baseUrl, path = '') {
  const normalizedBase = String(baseUrl || '').replace(/\/+$/, '')
  const normalizedPath = String(path || '')
  if (!normalizedPath) {
    return normalizedBase
  }
  return `${normalizedBase}${normalizedPath.startsWith('/') ? normalizedPath : `/${normalizedPath}`}`
}

function normalizeRetryEndpoint(endpoint = '') {
  const value = String(endpoint || '')
  if (/\/v1\/chat\/completions\/$/i.test(value)) {
    return value.replace(/\/+$/, '')
  }
  return value
}

function sanitizeModelAnswer(text = '') {
  let value = String(text || '')
  if (!value) {
    return ''
  }
  value = value.replace(/<think>[\s\S]*?<\/think>/gi, '')
  value = value.replace(/<\/?think>/gi, '')
  value = value.replace(/^\s*好的[，,。]?\s*/i, '')
  return value.trim()
}

function pickFirstString(container, keys = []) {
  if (!container || typeof container !== 'object') {
    return ''
  }
  for (let i = 0; i < keys.length; i += 1) {
    const value = container[keys[i]]
    if (typeof value === 'string' && value.trim()) {
      return value.trim()
    }
  }
  return ''
}

function normalizeStringList(value) {
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (typeof item === 'string') {
          return item.trim()
        }
        if (item && typeof item === 'object') {
          return pickFirstString(item, ['title', 'name', 'label', 'source', 'url', 'content'])
        }
        return ''
      })
      .filter(Boolean)
  }
  if (typeof value === 'string' && value.trim()) {
    return [value.trim()]
  }
  return []
}

function extractOpenAIAnswer(payload) {
  const choices = payload && Array.isArray(payload.choices) ? payload.choices : []
  if (!choices.length) {
    return ''
  }
  const firstChoice = choices[0] || {}
  const message = firstChoice.message || {}
  if (typeof message.content === 'string' && message.content.trim()) {
    return sanitizeModelAnswer(message.content)
  }
  if (Array.isArray(message.content)) {
    const joinedContent = message.content
      .map((item) => {
        if (typeof item === 'string') {
          return item
        }
        if (item && typeof item === 'object') {
          return pickFirstString(item, ['text', 'content'])
        }
        return ''
      })
      .join('')
      .trim()
    if (joinedContent) {
      return sanitizeModelAnswer(joinedContent)
    }
  }
  if (typeof message.reasoning_content === 'string' && message.reasoning_content.trim()) {
    return sanitizeModelAnswer(message.reasoning_content)
  }
  if (Array.isArray(firstChoice.delta)) {
    const deltaText = firstChoice.delta
      .map((item) => {
        if (typeof item === 'string') {
          return item
        }
        if (item && typeof item === 'object') {
          return pickFirstString(item, ['text', 'content'])
        }
        return ''
      })
      .join('')
      .trim()
    if (deltaText) {
      return sanitizeModelAnswer(deltaText)
    }
  }
  const delta = firstChoice.delta || {}
  if (typeof delta.content === 'string' && delta.content.trim()) {
    return sanitizeModelAnswer(delta.content)
  }
  if (typeof delta.reasoning_content === 'string' && delta.reasoning_content.trim()) {
    return sanitizeModelAnswer(delta.reasoning_content)
  }
  if (typeof firstChoice.text === 'string' && firstChoice.text.trim()) {
    return sanitizeModelAnswer(firstChoice.text)
  }
  return sanitizeModelAnswer(pickFirstString(firstChoice, ['text']))
}

function parseRagResponse(rawData, endpoint) {
  let payload = rawData
  if (typeof payload === 'string') {
    try {
      payload = JSON.parse(payload)
    } catch (e) {
      const plainText = payload.trim()
      return {
        answer: plainText,
        context: '',
        sources: [],
        relatedQuestions: [],
        endpointLabel: endpoint
      }
    }
  }

  if (!payload || typeof payload !== 'object') {
    return {
      answer: '',
      context: '',
      sources: [],
      relatedQuestions: [],
      endpointLabel: endpoint
    }
  }

  const nestedData = payload.data && typeof payload.data === 'object' ? payload.data : {}
  const answer = pickFirstString(payload, ['answer', 'response', 'content', 'text', 'result'])
    || pickFirstString(nestedData, ['answer', 'response', 'content', 'text', 'result'])
    || extractOpenAIAnswer(payload)
    || extractOpenAIAnswer(nestedData)
  const context = pickFirstString(payload, ['context', 'retrieved_context'])
    || pickFirstString(nestedData, ['context', 'retrieved_context'])
  const sources = normalizeStringList(
    payload.sources || payload.documents || payload.references
      || nestedData.sources || nestedData.documents || nestedData.references
  )
  const relatedQuestions = normalizeStringList(
    payload.related_questions || payload.relatedQuestions || payload.questions
      || nestedData.related_questions || nestedData.relatedQuestions || nestedData.questions
  )

  return {
    answer: answer || context,
    context,
    sources,
    relatedQuestions,
    endpointLabel: endpoint
  }
}

function getContextPreview(context = '') {
  const normalized = String(context || '').replace(/\s+/g, ' ').trim()
  if (!normalized) {
    return ''
  }
  if (normalized.length <= 120) {
    return normalized
  }
  return `${normalized.slice(0, 120)}...`
}

function normalizeMatchText(text = '') {
  return String(text || '')
    .toLowerCase()
    .replace(/\s+/g, '')
    .replace(/[，,。！？?、；;：:“”"'（）()【】\[\]<>《》\-]/g, '')
}

function isFitnessQuestion(question = '') {
  return /动作|训练|怎么做|怎么练|练胸|练背|练腿|练肩|练手臂|热身|拉伸|发力|呼吸|重量|组数|次数|卧推|深蹲|硬拉|划船|引体|下拉|弯举|推举|飞鸟|夹胸|臀推|倒蹬|史密斯|哑铃|杠铃|器械/u.test(String(question || ''))
}

function getEquipmentMatchScore(item = {}, question = '') {
  const normalizedQuestion = normalizeMatchText(question)
  const name = String(item.name || '')
  let score = 0
  if (!normalizedQuestion || !name) {
    return score
  }
  if (normalizedQuestion.includes(normalizeMatchText(name))) {
    score += 120
  }
  if (/史密斯/u.test(name) && /史密斯/u.test(question)) score += 45
  if (/卧推/u.test(name) && /卧推/u.test(question)) score += 40
  if (/深蹲|哈克/u.test(name) && /深蹲|哈克/u.test(question)) score += 40
  if (/硬拉/u.test(name) && /硬拉/u.test(question)) score += 40
  if (/划船/u.test(name) && /划船/u.test(question)) score += 40
  if (/下拉|引体/u.test(name) && /下拉|引体/u.test(question)) score += 40
  if (/推举|推肩/u.test(name) && /推举|推肩/u.test(question)) score += 35
  if (/飞鸟/u.test(name) && /飞鸟/u.test(question)) score += 35
  if (/侧平举/u.test(name) && /侧平举/u.test(question)) score += 35
  if (/夹胸/u.test(name) && /夹胸/u.test(question)) score += 35
  if (/弯举/u.test(name) && /弯举/u.test(question)) score += 35
  if (/屈伸/u.test(name) && /屈伸/u.test(question)) score += 35
  if (/臀推/u.test(name) && /臀推/u.test(question)) score += 35
  if (/倒蹬/u.test(name) && /倒蹬/u.test(question)) score += 35
  if (/跑步机/u.test(name) && /跑步机/u.test(question)) score += 35
  if (/椭圆机/u.test(name) && /椭圆机/u.test(question)) score += 35
  if (/登山机/u.test(name) && /登山机/u.test(question)) score += 35

  if (/练胸|胸部/u.test(question) && item.part_name === '胸部') score += 28
  if (/练背|背部/u.test(question) && item.part_name === '背部') score += 28
  if (/练腿|臀腿|深蹲/u.test(question) && item.part_name === '臀腿') score += 28
  if (/练肩|肩部/u.test(question) && item.part_name === '肩部') score += 28
  if (/练手臂|二头|三头|手臂/u.test(question) && item.part_name === '手臂') score += 28
  if (/有氧|跑步|减脂/u.test(question) && item.part_name === '有氧') score += 20
  if (/器械/u.test(question)) score += 5

  return score
}

function buildLocalFitnessReply(question = '') {
  if (!isFitnessQuestion(question)) {
    return null
  }
  const matchedList = (Array.isArray(EQUIPMENT_LIBRARY) ? EQUIPMENT_LIBRARY : [])
    .map((item) => ({
      ...item,
      _score: getEquipmentMatchScore(item, question)
    }))
    .filter((item) => item._score > 0)
    .sort((a, b) => b._score - a._score)

  if (!matchedList.length) {
    return null
  }

  const topItems = matchedList.slice(0, matchedList[0]._score >= 100 ? 1 : 2)
  const answer = topItems.map((item, index) => {
    const prefix = topItems.length > 1 ? `${index + 1}. ` : ''
    return `${prefix}${item.name}
目标肌群：${item.target_muscles || '待补充'}
训练定位：${item.training_focus || '基础专项训练'}
动作要点：${item.action_tips || '训练时先用轻重量熟悉动作轨迹，再逐步提升强度。'}
注意事项：${item.precautions || '训练中保持动作可控，如有明显关节不适应立即停止。'}`
  }).join('\n\n')

  const context = topItems.map((item) => `${item.name}：${item.description || item.action_tips || ''}`).join('\n')
  const relatedQuestions = topItems.map((item) => `${item.name}的常见错误有哪些？`)

  return {
    answer,
    context,
    sources: topItems.map((item) => item.name),
    relatedQuestions,
    endpointLabel: 'local-fitness-library'
  }
}

function buildHistoryMessages(messages = []) {
  if (!Array.isArray(messages)) {
    return []
  }
  return messages
    .filter((item) => item && item.type && item.content)
    .slice(-10)
    .map((item) => ({
      role: item.type === 'user' ? 'user' : 'assistant',
      content: item.content
    }))
}

function buildVllmMessages(question, history = []) {
  const fitnessPrompt = /动作|训练|练胸|练背|练腿|肩|手臂|深蹲|卧推|硬拉|史密斯|器械|增肌|减脂|热身|拉伸/i.test(question)
    ? '你是美式铁馆的小程序 AI 健身教练。请直接输出最终答案，不要输出思考过程、分析过程、推理过程、<think> 标签或草稿。当前用户问的是训练动作或器械使用问题，请优先给出标准动作要点、呼吸节奏、常见错误、适合新手的重量建议和安全注意事项。'
    : '你是美式铁馆的小程序 AI 健身教练。请直接输出最终答案，不要输出思考过程、分析过程、推理过程、<think> 标签或草稿。优先回答训练动作、器械使用、训练安排、课程建议等健身问题；回答要简洁、专业、可执行，优先给出动作要点和注意事项。'
  const messages = [{
    role: 'system',
    content: fitnessPrompt
  }]
  if (Array.isArray(history) && history.length) {
    messages.push(...history)
  }
  messages.push({
    role: 'user',
    content: question
  })
  return messages
}

Page({
  data: {
    inputValue: '',
    messages: [],
    quickTags: [],
    welcomeMessage: '欢迎使用智能助手。',
    lastId: 'msg-0',
    focusComposer: false,
    loading: false,
    chatStatus: 'loading',
    chatStatusText: '会话加载中...',
    ragBaseUrl: '/api/bot/chat/',
    vllmBaseUrl: DIRECT_VLLM_BASE_URL,
    lastRagEndpoint: '',
    ragStatusText: '已切换到 Django 统一网关模式'
  },

  onLoad() {
    this.loadPageConfig().finally(() => {
      this.loadConversation()
    })
  },

  onUnload() {},

  loadPageConfig() {
    return get('bot/config/')
      .then((config) => {
        const title = (config && config.page_title) || 'AI 教练'
        wx.setNavigationBarTitle({ title })
        this.setData({
          welcomeMessage: (config && config.welcome_message) || this.data.welcomeMessage,
          quickTags: Array.isArray(config && config.quick_questions) && config.quick_questions.length
            ? config.quick_questions
            : this.data.quickTags
        })
      })
      .catch(() => {
        wx.setNavigationBarTitle({ title: 'AI 教练' })
      })
  },

  loadConversation() {
    this.setData({
      chatStatus: 'loading',
      chatStatusText: '会话加载中...'
    })
    return this.fetchHistory()
      .then((historyMessages) => {
        const hasHistory = Array.isArray(historyMessages) && historyMessages.length > 0
        const defaultMessages = [{
          id: 'welcome',
          type: 'ai',
          content: this.data.welcomeMessage
        }]
        this.setData({
          messages: hasHistory ? historyMessages : defaultMessages,
          chatStatus: 'success',
          chatStatusText: ''
        })
        this.scrollToBottom()
      })
      .catch((err) => {
        this.setData({
          messages: [{
            id: 'welcome-fallback',
            type: 'ai',
            content: this.data.welcomeMessage
          }],
          chatStatus: 'success',
          chatStatusText: ''
        })
      })
  },

  fetchHistory() {
    return get('bot/history/').then((payload) => {
      const source = Array.isArray(payload)
        ? payload
        : Array.isArray(payload && payload.messages)
          ? payload.messages
          : Array.isArray(payload && payload.list)
            ? payload.list
            : []
      return source
        .map((item, index) => this.mapMessage(item, index))
        .filter(Boolean)
    })
  },

  mapMessage(item, index) {
    const content = item && (item.content || item.message || item.text || item.answer)
    if (!content) {
      return null
    }
    const role = item.role || item.type || item.sender
    const type = role === 'user' ? 'user' : 'ai'
    return {
      id: item.id || `history-${index}`,
      type,
      content
    }
  },

  scrollToBottom() {
    this.setData({
      lastId: `msg-${this.data.messages.length - 1}`
    })
  },

  onInput(e) {
    this.setData({
      inputValue: e.detail.value
    })
  },

  onTapComposer() {
    if (!this.data.focusComposer) {
      this.setData({ focusComposer: true })
    }
  },

  onComposerFocus() {
    this.setData({ focusComposer: true })
    this.scrollToBottom()
  },

  onComposerBlur() {
    this.setData({ focusComposer: false })
  },

  onTagTap(e) {
    const text = e.currentTarget.dataset.text
    this.sendMessage(text)
  },

  onSend() {
    const content = this.data.inputValue.trim()
    if (!content) {
      return
    }
    this.sendMessage(content, true)
  },

  sendMessage(content, clearInput = false) {
    const userMsg = {
      id: Date.now(),
      type: 'user',
      content
    }
    const newMessages = [...this.data.messages, userMsg]
    this.setData({
      messages: newMessages,
      inputValue: clearInput ? '' : this.data.inputValue,
      lastId: `msg-${newMessages.length - 1}`,
      loading: true,
      focusComposer: false
    })

    return this.requestDirectRag(content)
      .then((payload) => {
        const aiText = payload && payload.answer
        if (!aiText) {
          throw new Error('AI 未返回有效内容')
        }
        const relatedQuestions = Array.isArray(payload && (payload.related_questions || payload.relatedQuestions))
          ? (payload.related_questions || payload.relatedQuestions)
          : []
        const aiMsg = {
          id: Date.now() + 1,
          type: 'ai',
          content: aiText,
          sources: Array.isArray(payload && payload.sources) ? payload.sources.slice(0, 3) : [],
          relatedQuestions: relatedQuestions.slice(0, 5),
          contextPreview: getContextPreview(payload && payload.context),
          endpoint: payload && payload.endpointLabel ? payload.endpointLabel : ''
        }
        const updatedMessages = [...this.data.messages, aiMsg]
        this.setData({
          messages: updatedMessages,
          loading: false,
          quickTags: relatedQuestions.length ? relatedQuestions.slice(0, 5) : this.data.quickTags,
          lastId: `msg-${updatedMessages.length - 1}`,
          lastRagEndpoint: aiMsg.endpoint,
          ragStatusText: aiMsg.endpoint ? `后台联调成功：${aiMsg.endpoint}` : '后台联调成功'
        })
      })
      .catch((err) => {
        // 请求失败时，移除刚才乐观添加的用户消息，并恢复输入框内容
        const restoredMessages = this.data.messages.filter(m => m.id !== userMsg.id)
        this.setData({
          messages: restoredMessages,
          inputValue: content,
          loading: false,
          lastId: restoredMessages.length ? `msg-${restoredMessages.length - 1}` : 'msg-0',
          ragStatusText: (err && err.debugMessage) || (err && err.message) || '后台联调失败，请检查 Django 与 RAG 服务'
        })
        wx.showToast({ title: (err && err.message) || '网络异常或服务不可用，请重试', icon: 'none' })
      })
  },

  requestDirectRag(question) {
    return post('bot/chat/', {
      query: question,
      message: question
    }, {
      timeout: 90000
    }).then((payload) => ({
      ...payload,
      endpointLabel: '/api/bot/chat/'
    }))
  },

  buildRequestPayload(endpoint, question, history) {
    if (/\/v1\/chat\/completions\/?$/i.test(endpoint)) {
      return {
        model: DIRECT_VLLM_MODEL,
        messages: buildVllmMessages(question, history),
        temperature: 0.7,
        max_tokens: 1024,
        top_p: 0.9,
        stream: false
      }
    }

    return {
      question,
      message: question,
      system_prompt: '你是一个 helpful 的中文 AI 助手，请简洁、准确地回答用户问题。',
      history,
      temperature: 0.7,
      max_tokens: 1024,
      top_p: 0.9,
      query: question,
      top_k: 3,
      k: 3,
      rerank_top_n: 3
    }
  },

  requestRagEndpoint(endpoint, data) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: endpoint,
        method: 'POST',
        timeout: 20000,
        header: {
          'Content-Type': 'application/json'
        },
        data,
        success: (res) => {
          const statusCode = res.statusCode || 0
          if ((statusCode === 307 || statusCode === 308) && /\/v1\/chat\/completions\/?$/i.test(endpoint)) {
            const redirectedEndpoint = normalizeRetryEndpoint(endpoint)
            if (redirectedEndpoint !== endpoint) {
              this.requestRagEndpoint(redirectedEndpoint, data)
                .then(resolve)
                .catch(reject)
              return
            }
          }
          if (statusCode < 200 || statusCode >= 300) {
            reject({
              message: `${endpoint} 返回状态码 ${statusCode}`
            })
            return
          }

          const parsed = parseRagResponse(res.data, endpoint)
          if (!parsed.answer) {
            reject({
              message: `${endpoint} 已响应，但未返回可识别的 answer/context`,
              stopFallback: /\/v1\/chat\/completions\/?$/i.test(endpoint)
            })
            return
          }
          resolve(parsed)
        },
        fail: (err) => {
          const rawMessage = err && err.errMsg ? err.errMsg : ''
          let message = `${endpoint} 请求失败`
          if (/not in domain list/i.test(rawMessage)) {
            message = '请求失败：FastAPI 域名未加入小程序合法域名白名单'
          } else if (/timeout/i.test(rawMessage)) {
            message = `请求超时：${endpoint}`
          } else if (/fail ssl handshake/i.test(rawMessage)) {
            message = `HTTPS 证书或握手异常：${endpoint}`
          } else if (rawMessage) {
            message = `${endpoint} 请求失败：${rawMessage}`
          }
          reject({ message })
        }
      })
    })
  }
})
