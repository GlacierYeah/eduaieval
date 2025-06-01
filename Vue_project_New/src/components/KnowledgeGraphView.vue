<template>
  <div class="knowledge-graph-view">
    <div id="knowledge-graph-container" class="graph-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
})

let chartInstance = null

// 初始化图表
const initChart = () => {
  const el = document.getElementById('knowledge-graph-container')
  if (!el) return
  
  chartInstance = echarts.init(el)
  
  // 设置窗口调整时图表自适应
  window.addEventListener('resize', () => {
    if (chartInstance) {
      chartInstance.resize()
    }
  })
  
  // 更新图表数据
  updateChart()
}

// 构建知识图谱数据
const formatGraphData = (data) => {
  if (!data) return { nodes: [], links: [] }
  
  const nodes = []
  const links = []
  
  // 递归构建节点和连接
  const processNode = (node, parentId = null, level = 0) => {
    if (!node) return null
    
    const nodeId = `${node.name}_${level}_${Math.random().toString(36).substr(2, 9)}`
    
    // 添加节点
    nodes.push({
      id: nodeId,
      name: node.name,
      value: node.description || '',
      symbolSize: Math.max(30 - level * 4, 12),  // 根据层级调整节点大小，但确保最小尺寸
      category: level,
      itemStyle: {
        color: level === 0 ? '#FF6E6E' : level === 1 ? '#5E9CFF' : '#70D1AA'
      }
    })
    
    // 如果有父节点，添加连接
    if (parentId) {
      links.push({
        source: parentId,
        target: nodeId,
        lineStyle: {
          width: Math.max(3 - level * 0.5, 1),  // 根据层级调整连线粗细
          opacity: 0.8,
          curveness: 0.1 + level * 0.05,  // 层级越深，曲度越大
          color: level === 1 ? '#8DB4FF' : '#A0E3C0'
        }
      })
    }
    
    // 处理子节点
    if (node.children && node.children.length > 0) {
      node.children.forEach(child => {
        processNode(child, nodeId, level + 1)
      })
    }
    
    return nodeId
  }
  
  // 从根节点开始处理
  processNode(data, null)
  
  return { nodes, links }
}

// 更新图表数据
const updateChart = () => {
  if (!chartInstance || !props.data) return
  
  const graphData = formatGraphData(props.data)
  
  const options = {
    title: {
      text: props.data.name || '知识图谱',
      top: 'top',
      left: 'center',
      textStyle: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#333'
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.value) {
          return `<div style="font-weight:bold;color:#444;margin-bottom:5px">${params.name}</div>
                  <div style="color:#666">${params.value}</div>`
        }
        return `<div style="font-weight:bold;color:#444">${params.name}</div>`
      },
      backgroundColor: 'rgba(255,255,255,0.9)',
      borderColor: '#eee',
      borderWidth: 1,
      padding: 10,
      textStyle: {
        color: '#333'
      }
    },
    legend: {
      show: false
    },
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: graphData.nodes,
        links: graphData.links,
        categories: Array.from({ length: 10 }, (_, i) => ({ name: `Level ${i}` })),
        roam: true,
        draggable: true,
        cursor: 'pointer',
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          fontSize: 12,
          color: '#333',
          backgroundColor: 'rgba(255,255,255,0.7)',
          padding: [3, 5],
          borderRadius: 3
        },
        emphasis: {
          focus: 'adjacency',
          scale: true,
          label: {
            fontSize: 13,
            fontWeight: 'bold'
          },
          lineStyle: {
            width: 3,
            opacity: 0.9
          }
        },
        force: {
          repulsion: 200,
          edgeLength: [80, 150],
          gravity: 0.1
        },
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 8]
      }
    ]
  }
  
  chartInstance.setOption(options)
  
  // 添加点击事件
  chartInstance.on('click', (params) => {
    if (params.dataType === 'node') {
      // 点击节点时，聚焦显示该节点及其相邻节点
      chartInstance.dispatchAction({
        type: 'focusNodeAdjacency',
        seriesIndex: 0,
        dataIndex: params.dataIndex
      });
    }
  });
}

// 监听数据变化
watch(() => props.data, updateChart, { deep: true })

// 组件挂载时初始化图表
onMounted(() => {
  initChart()
})
</script>

<style scoped>
.knowledge-graph-view {
  width: 100%;
  height: 100%;
  position: relative;
}

.graph-container {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  background-color: #fafafa;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
}
</style> 