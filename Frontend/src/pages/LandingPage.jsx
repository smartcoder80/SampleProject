import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getMe, logout } from '../api'
import styles from './LandingPage.module.css'

export default function LandingPage() {
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMe()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        navigate('/login')
      })
      .finally(() => setLoading(false))
  }, [navigate])

  async function handleSignOut() {
    await logout()
    navigate('/login')
  }

  if (loading) {
    return (
      <div className={styles.loader}>
        <div className={styles.spinner} />
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <header className={styles.navbar}>
        <div className={styles.navBrand}>Sample App</div>
        <div className={styles.navRight}>
          {user && (
            <span className={styles.greeting}>
              Welcome, <strong>{user.username}</strong>
            </span>
          )}
          <button className={styles.signoutBtn} onClick={handleSignOut}>
            Sign Out
          </button>
        </div>
      </header>

      <main className={styles.main}>
        <section className={styles.hero}>
          <h1 className={styles.heroTitle}>Welcome to Sample App</h1>
          <p className={styles.heroSubtitle}>
            You are now signed in. Start building something amazing.
          </p>
        </section>

        {user && (
          <section className={styles.profileCard}>
            <h2>Your Profile</h2>
            <div className={styles.profileGrid}>
              <div className={styles.profileItem}>
                <span className={styles.profileLabel}>Username</span>
                <span className={styles.profileValue}>{user.username}</span>
              </div>
              <div className={styles.profileItem}>
                <span className={styles.profileLabel}>Email</span>
                <span className={styles.profileValue}>{user.email}</span>
              </div>
              <div className={styles.profileItem}>
                <span className={styles.profileLabel}>Member Since</span>
                <span className={styles.profileValue}>
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </span>
              </div>
            </div>
          </section>
        )}

        <section className={styles.cards}>
          <div className={styles.card}>
            <div className={styles.cardIcon}>🚀</div>
            <h3>Get Started</h3>
            <p>Explore features and start your first project.</p>
          </div>
          <div className={styles.card}>
            <div className={styles.cardIcon}>📊</div>
            <h3>Dashboard</h3>
            <p>View your activity and project statistics.</p>
          </div>
          <div className={styles.card}>
            <div className={styles.cardIcon}>⚙️</div>
            <h3>Settings</h3>
            <p>Manage your account preferences and profile.</p>
          </div>
        </section>
      </main>
    </div>
  )
}
