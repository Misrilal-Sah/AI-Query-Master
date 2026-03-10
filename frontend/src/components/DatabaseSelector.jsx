import { SiMysql } from 'react-icons/si'

export default function DatabaseSelector() {
  return (
    <div className="db-selector">
      <button className="db-option active">
        <SiMysql style={{ fontSize: '1.1rem' }} />
        MySQL
      </button>
    </div>
  )
}
