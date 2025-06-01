<template>
  <div class="knowledge-list-view">
    <div v-if="flattenedData.length > 0">
      <el-input
        v-model="searchQuery"
        placeholder="搜索知识点..."
        clearable
        prefix-icon="el-icon-search"
        class="search-input"
      ></el-input>
      
      <div class="knowledge-stats">
        <el-tag type="info" effect="plain">共 {{ flattenedData.length }} 个知识点</el-tag>
        <el-tag v-if="filteredData.length !== flattenedData.length" type="warning" effect="plain">
          匹配 {{ filteredData.length }} 个结果
        </el-tag>
      </div>
      
      <el-tree
        :data="treeData"
        :props="defaultProps"
        default-expand-all
        :filter-node-method="filterNode"
        ref="tree"
        node-key="id"
        :expand-on-click-node="false"
        highlight-current
        class="knowledge-tree"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label" :class="{ 'has-description': data.description }">{{ node.label }}</span>
            <el-tooltip v-if="data.description" effect="light" placement="right" :content="data.description">
              <el-tag size="small" type="info">详情</el-tag>
            </el-tooltip>
          </div>
        </template>
      </el-tree>
    </div>
    <el-empty v-else description="暂无知识点数据"></el-empty>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

const searchQuery = ref('')
const tree = ref(null)

// 将知识点树扁平化为一维数组以便搜索
const flattenedData = computed(() => {
  const result = []
  
  const traverse = (node, path = []) => {
    if (!node) return
    
    const currentNode = {
      id: node.name + '_' + Math.random().toString(36).substr(2, 9),
      name: node.name,
      description: node.description || '',
      path: [...path]
    }
    
    result.push(currentNode)
    
    if (node.children && node.children.length > 0) {
      node.children.forEach(child => traverse(child, [...path, node.name]))
    }
  }
  
  traverse(props.data)
  return result
})

// 过滤后的数据
const filteredData = computed(() => {
  if (!searchQuery.value) return flattenedData.value
  
  const query = searchQuery.value.toLowerCase()
  return flattenedData.value.filter(item => 
    item.name.toLowerCase().includes(query) || 
    (item.description && item.description.toLowerCase().includes(query))
  )
})

// 构建树状数据
const treeData = computed(() => {
  if (!props.data) return []
  
  const processNode = (node) => {
    if (!node) return null
    
    const result = {
      id: node.name + '_' + Math.random().toString(36).substr(2, 9),
      label: node.name,
      description: node.description || ''
    }
    
    if (node.children && node.children.length > 0) {
      result.children = node.children.map(processNode).filter(Boolean)
    }
    
    return result
  }
  
  return [processNode(props.data)]
})

// 树组件属性
const defaultProps = {
  children: 'children',
  label: 'label'
}

// 过滤节点方法
const filterNode = (value, data) => {
  if (!value) return true
  
  const query = value.toLowerCase()
  return data.label.toLowerCase().includes(query) || 
         (data.description && data.description.toLowerCase().includes(query))
}

// 监听搜索输入变化
watch(searchQuery, val => {
  nextTick(() => {
    if (tree.value) {
      tree.value.filter(val)
    }
  })
})
</script>

<style scoped>
.knowledge-list-view {
  height: 100%;
  padding: 10px 0;
}

.search-input {
  margin-bottom: 15px;
}

.knowledge-stats {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.knowledge-tree {
  margin-top: 15px;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 10px;
  background-color: #fff;
  max-height: 550px;
  overflow-y: auto;
}

.knowledge-tree :deep(.el-tree-node__content) {
  height: auto;
  min-height: 32px;
  padding: 5px 0;
}

.knowledge-tree :deep(.el-tree-node.is-current > .el-tree-node__content) {
  background-color: #ecf5ff;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 10px;
}

.node-label {
  word-break: break-word;
  padding-right: 15px;
}

.node-label.has-description {
  font-weight: bold;
  color: #303133;
}

/* 滚动条美化 */
.knowledge-tree::-webkit-scrollbar {
  width: 6px;
}

.knowledge-tree::-webkit-scrollbar-thumb {
  background-color: #c0c4cc;
  border-radius: 3px;
}

.knowledge-tree::-webkit-scrollbar-track {
  background-color: #f5f7fa;
}
</style> 