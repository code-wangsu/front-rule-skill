/** 导入 Vue 响应式状态，供独立查询 hook 暴露加载状态。 */
import { ref } from 'vue'

/** 导出只负责列表查询的 hook；response.data.page.records 必须已由契约确认。 */
export function useRecordList(requestPage) {
  /** 正式接口返回的当前记录列表。 */
  const records = ref([])
  /** 当前查询是否正在执行。 */
  const loading = ref(false)

  /** 查询记录并收尾加载状态；请求字段由调用方按已确认契约提供。 */
  async function queryRecords(params) {
    if (loading.value) {
      return
    }
    loading.value = true
    try {
      // 保留接口完整响应用于按已确认层级读取记录。
      const response = await requestPage(params)
      records.value = response.data.page.records
    } catch (error) {
      // 错误交由调用方处理，避免与 HTTP 拦截器重复提示。
      throw error
    } finally {
      loading.value = false
    }
  }

  return { records, loading, queryRecords }
}
