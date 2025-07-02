import React, { useState } from 'react'

const DataContext = React.createContext([{}, () => {}])

const DataProvider = ({ children }) => {
  const [data, setData] = useState(false)
  const [uploadDoc, setuploadDoc] = useState({})
  return (
    <DataContext.Provider value={[data, setData, uploadDoc, setuploadDoc]}>
      {children}
    </DataContext.Provider>
  )
}

export { DataContext, DataProvider }