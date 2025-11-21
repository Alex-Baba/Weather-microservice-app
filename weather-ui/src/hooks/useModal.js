import { useState, useRef, useEffect } from 'react'

export default function useModal(autoCloseSeconds = 5) {
  const [modalMessage, setModalMessage] = useState(null)
  const [countdown, setCountdown] = useState(0)
  const modalTimerRef = useRef(null)
  const intervalRef = useRef(null)

  useEffect(() => {
    if (modalTimerRef.current) {
      clearTimeout(modalTimerRef.current)
      modalTimerRef.current = null
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    if (modalMessage) {
      setCountdown(autoCloseSeconds)
      modalTimerRef.current = setTimeout(() => setModalMessage(null), autoCloseSeconds * 1000)
      intervalRef.current = setInterval(() => setCountdown((s) => (s > 0 ? s - 1 : 0)), 1000)
    } else {
      setCountdown(0)
    }

    return () => {
      if (modalTimerRef.current) clearTimeout(modalTimerRef.current)
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [modalMessage, autoCloseSeconds])

  const hide = () => {
    if (modalTimerRef.current) { clearTimeout(modalTimerRef.current); modalTimerRef.current = null }
    if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null }
    setCountdown(0)
    setModalMessage(null)
  }

  return { modalMessage, setModalMessage, hide, countdown }
}
