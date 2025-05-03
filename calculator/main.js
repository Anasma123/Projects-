document.addEventListener('DOMContentLoaded', function() {
  class Calculator {
      constructor(previousOperandElement, currentOperandElement) {
          this.previousOperandElement = previousOperandElement;
          this.currentOperandElement = currentOperandElement;
          this.memoryIndicator = document.querySelector('.memory-indicator');
          this.angleIndicator = document.querySelector('.angle-indicator');
          this.memoryValue = 0;
          this.angleUnit = 'deg';
          this.currentMode = 'basic';
          this.currentBase = 'dec';
          this.clear();
      }

      clear() {
          this.currentOperand = '0';
          this.previousOperand = '';
          this.operation = undefined;
          this.error = false;
          this.updateDisplay();
      }

      delete() {
          if (this.error) return;
          this.currentOperand = this.currentOperand.toString().slice(0, -1);
          if (this.currentOperand === '') {
              this.currentOperand = '0';
          }
          this.updateDisplay();
      }

      appendNumber(number) {
          if (this.error) return;
          if (number === '.' && this.currentOperand.includes('.') && this.currentBase === 'dec') return;
          
          if (this.currentBase !== 'dec') {
              if (this.currentBase === 'bin' && !['0', '1'].includes(number)) return;
              if (this.currentBase === 'oct' && !['0', '1', '2', '3', '4', '5', '6', '7'].includes(number)) return;
              if (this.currentBase === 'hex' && !['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'].includes(number.toUpperCase())) return;
          }
          
          if (this.currentOperand === '0' && number !== '.') {
              this.currentOperand = number.toString();
          } else {
              this.currentOperand = this.currentOperand.toString() + number.toString();
          }
          this.updateDisplay();
      }

      chooseOperation(operation) {
          if (this.error || this.currentOperand === '') return;
          if (this.previousOperand !== '') {
              this.compute();
          }
          this.operation = operation;
          this.previousOperand = this.currentOperand;
          this.currentOperand = '';
          this.updateDisplay();
      }

      compute() {
          if (this.error) return;
          let computation;
          const prev = this.convertToDecimal(this.previousOperand);
          const current = this.convertToDecimal(this.currentOperand);
          
          if (isNaN(prev) || isNaN(current)) {
              this.error = true;
              this.currentOperand = 'Error';
              this.updateDisplay();
              return;
          }

          switch (this.operation) {
              case '+':
                  computation = prev + current;
                  break;
              case '-':
                  computation = prev - current;
                  break;
              case '×':
                  computation = prev * current;
                  break;
              case '÷':
                  if (current === 0) {
                      this.error = true;
                      this.currentOperand = 'Error: Div by 0';
                      this.updateDisplay();
                      return;
                  }
                  computation = prev / current;
                  break;
              case '%':
              case 'mod':
                  computation = prev % current;
                  break;
              case 'x^y':
                  computation = Math.pow(prev, current);
                  break;
              case 'and':
                  computation = prev & current;
                  break;
              case 'or':
                  computation = prev | current;
                  break;
              case 'xor':
                  computation = prev ^ current;
                  break;
              case 'lsh':
                  computation = prev << current;
                  break;
              case 'rsh':
                  computation = prev >> current;
                  break;
              case 'nand':
                  computation = ~(prev & current);
                  break;
              case 'nor':
                  computation = ~(prev | current);
                  break;
              default:
                  return;
          }

          this.currentOperand = this.formatResult(this.convertFromDecimal(computation));
          this.operation = undefined;
          this.previousOperand = '';
          this.updateDisplay();
      }

      scientificOperation(operation) {
          if (this.error) return;
          let current = this.convertToDecimal(this.currentOperand);
          if (isNaN(current)) {
              this.error = true;
              this.currentOperand = 'Error';
              this.updateDisplay();
              return;
          }

          let computation;
          const value = this.angleUnit === 'deg' ? current * (Math.PI / 180) : current;

          switch (operation) {
              case 'sin':
                  computation = Math.sin(value);
                  break;
              case 'cos':
                  computation = Math.cos(value);
                  break;
              case 'tan':
                  computation = Math.tan(value);
                  if (isNaN(computation) || !isFinite(computation)) {
                      this.error = true;
                      this.currentOperand = 'Error';
                      this.updateDisplay();
                      return;
                  }
                  break;
              case 'sinh':
                  computation = Math.sinh(value);
                  break;
              case 'cosh':
                  computation = Math.cosh(value);
                  break;
              case 'tanh':
                  computation = Math.tanh(value);
                  break;
              case 'log':
                  if (current <= 0) {
                      this.error = true;
                      this.currentOperand = 'Error: Invalid log';
                      this.updateDisplay();
                      return;
                  }
                  computation = Math.log10(current);
                  break;
              case 'ln':
                  if (current <= 0) {
                      this.error = true;
                      this.currentOperand = 'Error: Invalid ln';
                      this.updateDisplay();
                      return;
                  }
                  computation = Math.log(current);
                  break;
              case '√':
                  if (current < 0) {
                      this.error = true;
                      this.currentOperand = 'Error: Invalid sqrt';
                      this.updateDisplay();
                      return;
                  }
                  computation = Math.sqrt(current);
                  break;
              case 'x²':
                  computation = Math.pow(current, 2);
                  break;
              case 'x³':
                  computation = Math.pow(current, 3);
                  break;
              case '10^x':
                  computation = Math.pow(10, current);
                  break;
              case 'exp':
                  computation = Math.exp(current);
                  break;
              case 'π':
                  computation = Math.PI;
                  break;
              case 'e':
                  computation = Math.E;
                  break;
              case 'rand':
                  computation = Math.random();
                  break;
              case 'fact':
                  if (!Number.isInteger(current) || current < 0) {
                      this.error = true;
                      this.currentOperand = 'Error: Invalid factorial';
                      this.updateDisplay();
                      return;
                  }
                  computation = this.factorial(current);
                  break;
              case '1/x':
                  if (current === 0) {
                      this.error = true;
                      this.currentOperand = 'Error: Div by 0';
                      this.updateDisplay();
                      return;
                  }
                  computation = 1 / current;
                  break;
              case '|x|':
                  computation = Math.abs(current);
                  break;
              case 'not':
                  computation = ~current;
                  break;
              default:
                  return;
          }

          this.currentOperand = this.formatResult(this.convertFromDecimal(computation));
          this.updateDisplay();
      }

      factorial(n) {
          if (n > 170) return Infinity; // Prevent overflow
          if (n === 0 || n === 1) return 1;
          let result = 1;
          for (let i = 2; i <= n; i++) {
              result *= i;
          }
          return result;
      }

      memoryOperation(operation) {
          if (this.error) return;
          const current = this.convertToDecimal(this.currentOperand);
          
          switch (operation) {
              case 'mc':
                  this.memoryValue = 0;
                  this.memoryIndicator.textContent = '';
                  break;
              case 'mr':
                  if (this.memoryValue !== 0) {
                      this.currentOperand = this.formatResult(this.convertFromDecimal(this.memoryValue));
                      this.updateDisplay();
                  }
                  break;
              case 'm+':
                  this.memoryValue += current;
                  this.memoryIndicator.textContent = 'M';
                  break;
              case 'm-':
                  this.memoryValue -= current;
                  this.memoryIndicator.textContent = 'M';
                  break;
              case 'ms':
                  this.memoryValue = current;
                  this.memoryIndicator.textContent = 'M';
                  break;
          }
      }

      convertToDecimal(value) {
          if (!value) return 0;
          try {
              if (this.currentBase === 'dec') return parseFloat(value);
              if (this.currentBase === 'bin') return parseInt(value, 2);
              if (this.currentBase === 'oct') return parseInt(value, 8);
              if (this.currentBase === 'hex') return parseInt(value, 16);
              return parseFloat(value);
          } catch {
              this.error = true;
              this.currentOperand = 'Error: Invalid input';
              this.updateDisplay();
              return NaN;
          }
      }

      convertFromDecimal(value) {
          if (isNaN(value) || !isFinite(value)) return 'Error';
          if (this.currentBase === 'dec') return value;
          if (this.currentBase === 'bin') return (value >>> 0).toString(2);
          if (this.currentBase === 'oct') return (value >>> 0).toString(8);
          if (this.currentBase === 'hex') return (value >>> 0).toString(16).toUpperCase();
          return value;
      }

      formatResult(value) {
          if (isNaN(value) || !isFinite(value)) return 'Error';
          if (this.currentBase !== 'dec') return value.toString().toUpperCase();
          // Format decimal numbers to avoid overflow and ensure readability
          const num = parseFloat(value);
          if (Math.abs(num) < 1e-10 && num !== 0) return num.toExponential(5);
          if (Math.abs(num) > 1e10) return num.toExponential(5);
          return Number(num.toFixed(10)).toString();
      }

      toggleAngleUnit() {
          if (this.error) return;
          this.angleUnit = this.angleUnit === 'deg' ? 'rad' : 'deg';
          this.angleIndicator.textContent = this.angleUnit.toUpperCase();
          document.querySelectorAll('.btn-angle-unit').forEach(btn => {
              btn.classList.remove('active');
          });
          document.querySelector(`[data-value="${this.angleUnit}"]`).classList.add('active');
      }

      setNumberBase(base) {
          if (this.error) return;
          this.currentBase = base;
          const current = this.convertToDecimal(this.currentOperand);
          this.currentOperand = this.formatResult(this.convertFromDecimal(current));
          this.updateDisplay();
          document.querySelectorAll('.btn-programmer').forEach(btn => {
              btn.classList.remove('active');
          });
          document.querySelector(`[data-value="${base}"]`).classList.add('active');
      }

      setMode(mode) {
          if (this.error) return;
          this.currentMode = mode;
          document.querySelectorAll('.calculator-buttons').forEach(panel => {
              panel.classList.remove('active-mode');
          });
          document.querySelector(`.${mode}-mode`).classList.add('active-mode');
          
          if (mode !== 'programmer') {
              this.setNumberBase('dec');
          } else {
              this.setNumberBase(this.currentBase);
          }
          this.clear();
      }

      updateDisplay() {
          this.currentOperandElement.innerText = this.currentOperand;
          if (this.error) {
              this.previousOperandElement.innerText = '';
          } else if (this.operation != null) {
              this.previousOperandElement.innerText = 
                  `${this.previousOperand} ${this.operation}`;
          } else {
              this.previousOperandElement.innerText = '';
          }
      }
  }

  // Initialize Calculator
  const previousOperandElement = document.querySelector('.previous-operand');
  const currentOperandElement = document.querySelector('.current-operand');
  const calculator = new Calculator(previousOperandElement, currentOperandElement);

  // Button Event Listeners
  document.querySelectorAll('[data-value]').forEach(button => {
      button.addEventListener('click', () => {
          const value = button.getAttribute('data-value');
          
          if (calculator.error && value !== 'clear') return;

          // Handle different types of operations
          if (!isNaN(value) || value === '.' || ['A', 'B', 'C', 'D', 'E', 'F'].includes(value.toUpperCase())) {
              calculator.appendNumber(value);
          } else if (['+', '-', '×', '÷', '%', 'mod', 'x^y', 'and', 'or', 'xor', 'lsh', 'rsh', 'nand', 'nor'].includes(value)) {
              calculator.chooseOperation(value);
          } else if (value === '=') {
              calculator.compute();
          } else if (value === 'clear') {
              calculator.clear();
          } else if (value === 'delete') {
              calculator.delete();
          } else if (['sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh', 'log', 'ln', 
                      '√', 'x²', 'x³', '10^x', 'exp', 'π', 'e', 'rand', 'fact', 
                      '1/x', '|x|', 'not'].includes(value)) {
              calculator.scientificOperation(value);
          } else if (['mc', 'mr', 'm+', 'm-', 'ms'].includes(value)) {
              calculator.memoryOperation(value);
          } else if (['deg', 'rad'].includes(value)) {
              calculator.toggleAngleUnit();
          } else if (['hex', 'dec', 'oct', 'bin'].includes(value)) {
              calculator.setNumberBase(value);
          } else if (['basic', 'scientific', 'programmer'].includes(value)) {
              calculator.setMode(value);
          }
      });
  });

  // Theme Switching
  document.querySelectorAll('.theme-btn').forEach(button => {
      button.addEventListener('click', () => {
          const theme = button.getAttribute('data-theme');
          document.body.setAttribute('data-theme', theme);
          localStorage.setItem('calculator-theme', theme);
          
          document.querySelectorAll('.theme-btn').forEach(btn => {
              btn.classList.remove('active');
          });
          button.classList.add('active');
      });
  });

  // Mode Switching
  document.querySelectorAll('.mode-btn').forEach(button => {
      button.addEventListener('click', () => {
          const mode = button.getAttribute('data-mode');
          calculator.setMode(mode);
          
          document.querySelectorAll('.mode-btn').forEach(btn => {
              btn.classList.remove('active');
          });
          button.classList.add('active');
      });
  });

  // Load saved theme
  const savedTheme = localStorage.getItem('calculator-theme') || 'light';
  document.body.setAttribute('data-theme', savedTheme);
  document.querySelector(`.theme-btn[data-theme="${savedTheme}"]`).classList.add('active');

  // Keyboard support
  document.addEventListener('keydown', (e) => {
      if (calculator.error && e.key !== 'Escape') return;
      const key = e.key;
      
      // Number keys
      if (!isNaN(key) || key === '.' || ['a', 'b', 'c', 'd', 'e', 'f'].includes(key.toLowerCase())) {
          const button = document.querySelector(`[data-value="${key.toUpperCase()}"]`) || document.querySelector(`[data-value="${key}"]`);
          if (button) button.click();
      } 
      // Operation keys
      else if (['+', '-', '*', '/', '%'].includes(key)) {
          let operation;
          if (key === '*') operation = '×';
          else if (key === '/') operation = '÷';
          else operation = key;
          
          const button = document.querySelector(`[data-value="${operation}"]`);
          if (button) button.click();
      } 
      // Other keys
      else if (key === 'Enter' || key === '=') {
          document.querySelector('[data-value="="]').click();
      } else if (key === 'Backspace') {
          document.querySelector('[data-value="delete"]').click();
      } else if (key === 'Escape') {
          document.querySelector('[data-value="clear"]').click();
      } else if (key.toLowerCase() === 'm' && e.ctrlKey) {
          if (e.key.toLowerCase() === 'c') document.querySelector('[data-value="mc"]').click();
          else if (e.key.toLowerCase() === 'r') document.querySelector('[data-value="mr"]').click();
          else if (e.key === '+') document.querySelector('[data-value="m+"]').click();
          else if (e.key === '-') document.querySelector('[data-value="m-"]').click();
          else if (e.key.toLowerCase() === 's') document.querySelector('[data-value="ms"]').click();
      } else if (key.toLowerCase() === 'd' && e.ctrlKey) {
          calculator.setMode('basic');
          document.querySelector('[data-mode="basic"]').click();
      } else if (key.toLowerCase() === 's' && e.ctrlKey) {
          calculator.setMode('scientific');
          document.querySelector('[data-mode="scientific"]').click();
      } else if (key.toLowerCase() === 'p' && e.ctrlKey) {
          calculator.setMode('programmer');
          document.querySelector('[data-mode="programmer"]').click();
      }
  });
});