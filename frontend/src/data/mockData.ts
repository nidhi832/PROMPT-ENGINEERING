export interface Transaction {
  id: string;
  title: string;
  category: 'Food' | 'Transport' | 'Shopping' | 'Bills' | 'Entertainment' | 'Health' | 'Education' | 'Salary' | 'Investment' | 'Other';
  amount: number; // positive for income, negative for expense
  date: string;
  account: string;
  icon: string;
  status?: 'verified' | 'review';
}

export interface BudgetCategory {
  category: string;
  spent: number;
  limit: number;
  color: string;
}

export interface AccountBalance {
  id: string;
  name: string;
  type: 'Bank' | 'Credit Card' | 'Cash' | 'Investment';
  balance: number;
  accountNumber: string;
  institution: string;
}

export const INITIAL_TRANSACTIONS: Transaction[] = [
  { id: 'T001', title: 'Salary Credit - Employer', category: 'Salary', amount: 85000, date: '12 Nov 2026', account: 'Salary Account', icon: '💼', status: 'verified' },
  { id: 'T002', title: 'IKEA Furnishing - Work Desk', category: 'Shopping', amount: -6450, date: '11 Nov 2026', account: 'Credit Card', icon: '🛍️', status: 'verified' },
  { id: 'T003', title: 'Swiggy Gourmet - Dinner with Friends', category: 'Food', amount: -1280, date: '11 Nov 2026', account: 'UPI', icon: '🍔', status: 'verified' },
  { id: 'T004', title: 'Uber Premier - Airport Transit', category: 'Transport', amount: -850, date: '10 Nov 2026', account: 'UPI', icon: '🚗', status: 'verified' },
  { id: 'T005', title: 'Cult.Fit Gym Membership Renewal', category: 'Health', amount: -2499, date: '09 Nov 2026', account: 'Credit Card', icon: '💊', status: 'verified' },
  { id: 'T006', title: 'Freelance UI Design Milestone', category: 'Salary', amount: 22000, date: '08 Nov 2026', account: 'Savings Account', icon: '🎨', status: 'verified' },
  { id: 'T007', title: 'Electricity & High-speed Wifi Bill', category: 'Bills', amount: -3200, date: '07 Nov 2026', account: 'Salary Account', icon: '🧾', status: 'verified' },
  { id: 'T008', title: 'Amazon Kindle & Tech Books', category: 'Education', amount: -1150, date: '06 Nov 2026', account: 'Credit Card', icon: '📚', status: 'verified' },
  { id: 'T009', title: 'PVR IMAX - Movie Night', category: 'Entertainment', amount: -940, date: '05 Nov 2026', account: 'UPI', icon: '🎬', status: 'verified' },
  { id: 'T010', title: 'Whole Foods & Weekly Organic Groceries', category: 'Food', amount: -3120, date: '04 Nov 2026', account: 'UPI', icon: '🍔', status: 'verified' },
  { id: 'T011', title: 'Starbucks Coffee & Snacks', category: 'Food', amount: -480, date: '03 Nov 2026', account: 'Cash', icon: '☕', status: 'verified' },
  { id: 'T012', title: 'Metro Smart Card Auto-recharge', category: 'Transport', amount: -500, date: '02 Nov 2026', account: 'UPI', icon: '🚇', status: 'verified' },
];

export const MONTHLY_CASHFLOW = [
  { month: 'Jul', income: 78000, expenses: 38400, savings: 39600 },
  { month: 'Aug', income: 82000, expenses: 41200, savings: 40800 },
  { month: 'Sep', income: 80000, expenses: 39800, savings: 40200 },
  { month: 'Oct', income: 85000, expenses: 44500, savings: 40500 },
  { month: 'Nov', income: 107000, expenses: 42860, savings: 64140 },
];

export const CATEGORY_EXPENSES = [
  { name: 'Food & Dining', value: 14250, color: '#FF665C', share: '33.2%' },
  { name: 'Shopping', value: 8900, color: '#FF78B9', share: '20.8%' },
  { name: 'Bills & Utilities', value: 7850, color: '#9B51E0', share: '18.3%' },
  { name: 'Transport', value: 4500, color: '#3498F3', share: '10.5%' },
  { name: 'Entertainment', value: 3400, color: '#FFA502', share: '7.9%' },
  { name: 'Health & Wellness', value: 2499, color: '#00C9A7', share: '5.8%' },
  { name: 'Education', value: 1461, color: '#2ED573', share: '3.5%' },
];

export const WEEKLY_SPENDING = [
  { day: 'Mon', amount: 1420 },
  { day: 'Tue', amount: 850 },
  { day: 'Wed', amount: 3200 },
  { day: 'Thu', amount: 1890 },
  { day: 'Fri', amount: 4650 },
  { day: 'Sat', amount: 7200 },
  { day: 'Sun', amount: 2840 },
];

export const BUDGET_CATEGORIES: BudgetCategory[] = [
  { category: 'Food & Dining', spent: 14250, limit: 16000, color: '#FF665C' },
  { category: 'Shopping', spent: 8900, limit: 8000, color: '#FF78B9' }, // over budget
  { category: 'Bills & Utilities', spent: 7850, limit: 9000, color: '#9B51E0' },
  { category: 'Transport', spent: 4500, limit: 5000, color: '#3498F3' },
  { category: 'Entertainment', spent: 3400, limit: 3000, color: '#FFA502' }, // over budget
  { category: 'Health', spent: 2499, limit: 3500, color: '#00C9A7' },
];


