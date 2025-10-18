import { useState } from 'react'
import Navbar from './components/Navbar'
import FinancialCards from './components/FinancialCards'
import SpendingChart from './components/SpendingChart'
import RecentTransactions from './components/RecentTransactions'
import AddTransactionModal from './components/AddTransactionModal'
import './App.css'

function App() {
  const [showModal, setShowModal] = useState(false)
  const [transactions, setTransactions] = useState([
    { id: 1, date: '2025-10-18', description: 'Salary', category: 'Income', amount: 5000, type: 'income' },
    { id: 2, date: '2025-10-15', description: 'Rent Payment', category: 'Housing', amount: -1200, type: 'expense' },
    { id: 3, date: '2025-10-14', description: 'Grocery Shopping', category: 'Food & Dining', amount: -150, type: 'expense' },
    { id: 4, date: '2025-10-12', description: 'Electric Bill', category: 'Utilities', amount: -80, type: 'expense' },
    { id: 5, date: '2025-10-10', description: 'Gas Station', category: 'Transportation', amount: -60, type: 'expense' },
    { id: 6, date: '2025-10-08', description: 'Movie Night', category: 'Entertainment', amount: -45, type: 'expense' },
    { id: 7, date: '2025-10-05', description: 'Online Shopping', category: 'Shopping', amount: -120, type: 'expense' },
    { id: 8, date: '2025-10-03', description: 'Doctor Visit', category: 'Healthcare', amount: -100, type: 'expense' },
  ])

  // Calculate financial data
  const totalIncome = transactions
    .filter(t => t.type === 'income')
    .reduce((sum, t) => sum + t.amount, 0)

  const expensesByCategory = transactions
    .filter(t => t.type === 'expense')
    .reduce((acc, t) => {
      acc[t.category] = (acc[t.category] || 0) + Math.abs(t.amount)
      return acc
    }, {})

  const totalExpenses = Object.values(expensesByCategory).reduce((a, b) => a + b, 0)
  const savings = totalIncome - totalExpenses

  const handleAddTransaction = (newTransaction) => {
    const transaction = {
      id: Date.now(),
      ...newTransaction,
      amount: newTransaction.type === 'expense' ? -Math.abs(newTransaction.amount) : Math.abs(newTransaction.amount)
    }
    setTransactions([transaction, ...transactions])
    setShowModal(false)
  }

  return (
    <div className="app">
      <Navbar onAddTransaction={() => setShowModal(true)} />
      
      <div className="container">
        <header className="header">
          <h1>💰 Financial Dashboard</h1>
          <div className="month-display">
            {new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </div>
        </header>

        <FinancialCards 
          totalIncome={totalIncome}
          totalExpenses={totalExpenses}
          savings={savings}
        />

        <div className="dashboard-grid">
          <SpendingChart expensesByCategory={expensesByCategory} />
          <RecentTransactions transactions={transactions} />
        </div>
      </div>

      {showModal && (
        <AddTransactionModal 
          onClose={() => setShowModal(false)}
          onAdd={handleAddTransaction}
        />
      )}
    </div>
  )
}

export default App
