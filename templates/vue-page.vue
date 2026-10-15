<template>
  <!-- 查询区：只负责输入已确认的筛选字段，向页面上抛查询事件。 -->
  <RecordQuery @search="queryRecords" />
  <!-- 列表区：直接消费接口 records，由独立组件承担列与分页展示。 -->
  <RecordTable :records="records" :loading="loading" />
</template>

<script setup>
/** 导入页面局部查询区；示例路径须替换为实际已存在文件。 */
import RecordQuery from './components/RecordQuery.vue'
/** 导入页面局部列表区；示例组件不代表项目已具有此封装。 */
import RecordTable from './components/RecordTable.vue'
/** 导入单一查询 hook，避免页面重复维护请求状态。 */
import { useRecordList } from './hooks/useRecordList'
/** 导入已确认契约的正式列表 API；使用模板前先核实此接口。 */
import { getRecordPage } from './api/records'

/** 当前页只组合查询与展示；请求字段和响应层级必须事先确认。 */
const { records, loading, queryRecords } = useRecordList(getRecordPage)
</script>

<style scoped lang="scss">
/* 页面结构优先使用当前项目已有布局组件，不复制新的全局布局体系。 */
</style>
