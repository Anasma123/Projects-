import React from 'react'
import './FinancialCards.css'

function FinancialCards({ totalIncome, totalExpenses, savings }) {
  return (
    <div className="financial-cards">
      <div className="card income">
        <div className="card-title">Total Income</div>
        <div className="card-amount">${totalIncome.toLocaleString()}</div>
        <div className="card-subtitle">This Month</div>
      </div>

      <div className="card expenses">
        <div className="card-title">Total Expenses</div>
        <div className="card-amount">${totalExpenses.toLocaleString()}</div>
        <div className="card-subtitle">This Month</div>
      </div>

      <div className="card savings">
        <div className="card-title">Savings</div>
        <div className="card-amount">${savings.toLocaleString()}</div>
        <div className="card-subtitle">Income - Expenses</div>
      </div>
    </div>
  )
}

export default FinancialCards
