import React from 'react'
import './Navbar.css'

function Navbar({ onAddTransaction }) {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <span className="navbar-icon">💳</span>
          <span className="navbar-title">Finance Tracker</span>
        </div>
        
        <div className="navbar-menu">
          <a href="#" className="navbar-link active">Dashboard</a>
          <a href="#" className="navbar-link">Transactions</a>
          <a href="#" className="navbar-link">Reports</a>
          <a href="#" className="navbar-link">Settings</a>
        </div>

        <button className="add-transaction-btn" onClick={onAddTransaction}>
          <span className="btn-icon">+</span>
          <span className="btn-text">Add Transaction</span>
        </button>
      </div>
    </nav>
  )
}

export default Navbar
