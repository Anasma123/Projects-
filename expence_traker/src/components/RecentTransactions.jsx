import React from 'react'
import './RecentTransactions.css'

function RecentTransactions({ transactions }) {
  return (
    <div className="transactions-section">
      <h2 className="transactions-title">📝 Recent Transactions</h2>
      <div className="transactions-list">
        {transactions.slice(0, 8).map((transaction) => (
          <div key={transaction.id} className="transaction-item">
            <div className="transaction-icon">
              {transaction.type === 'income' ? '💰' : '💸'}
            </div>
            <div className="transaction-details">
              <div className="transaction-description">{transaction.description}</div>
              <div className="transaction-meta">
                <span className="transaction-category">{transaction.category}</span>
                <span className="transaction-date">
                  {new Date(transaction.date).toLocaleDateString('en-US', { 
                    month: 'short', 
                    day: 'numeric' 
                  })}
                </span>
              </div>
            </div>
            <div className={`transaction-amount ${transaction.type}`}>
              {transaction.type === 'income' ? '+' : ''}
              ${Math.abs(transaction.amount).toLocaleString()}
            </div>
          </div>
        ))}
      </div>
      {transactions.length === 0 && (
        <div className="no-transactions">
          <p>No transactions yet</p>
          <p className="no-transactions-subtitle">Add your first transaction to get started!</p>
        </div>
      )}
    </div>
  )
}

export default RecentTransactions
