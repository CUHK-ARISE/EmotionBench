import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../pages/HomePage.vue'
import LeaderboardPage from '../pages/Leaderboard.vue'

const routes = [
  { path: '/', name: 'Home', component: HomePage },
  { path: '/leaderboard', name: 'Leaderboard', component: LeaderboardPage },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router