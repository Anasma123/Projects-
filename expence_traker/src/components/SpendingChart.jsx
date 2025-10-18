import React from 'react'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'react-chartjs-2'
import './SpendingChart.css'

ChartJS.register(ArcElement, Tooltip, Legend)

function SpendingChart({ expensesByCategory }) {
  const categories = Object.keys(expensesByCategory)
  const amounts = Object.values(expensesByCategory)
  const totalExpenses = amounts.reduce((a, b) => a + b, 0)

  const colors = [
    '#FF6384',
    '#36A2EB',
    '#FFCE56',
    '#4BC0C0',
    '#9966FF',
    '#FF9F40',
    '#FF6384',
    '#C9CBCF'
  ]

  const data = {
    labels: categories,
    datasets: [{
      data: amounts,
      backgroundColor: colors,
      borderWidth: 3,
      borderColor: '#fff'
    }]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || ''
            const value = context.parsed || 0
            const percentage = ((value / totalExpenses) * 100).toFixed(1)
            return `${label}: $${value.toLocaleString()} (${percentage}%)`
          }
        }
      }
    }
  }

  return (
    <div className="chart-section">
      <h2 className="chart-title">📊 Spending by Category</h2>
      <div className="chart-container">
        <Doughnut data={data} options={options} />
      </div>
      <div className="legend">
        {categories.map((category, index) => {
          const percentage = ((amounts[index] / totalExpenses) * 100).toFixed(1)
          return (
            <div key={category} className="legend-item">
              <div className="legend-color" style={{ backgroundColor: colors[index] }}></div>
              <div className="legend-text">{category}</div>
              <div className="legend-amount">${amounts[index].toLocaleString()} ({percentage}%)</div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default SpendingChart
