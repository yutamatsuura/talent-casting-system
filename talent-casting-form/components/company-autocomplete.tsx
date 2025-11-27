"use client"

import { useState, useRef, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { companies, type Company } from "@/lib/company-data"
import { Building2, MapPin } from "lucide-react"

type CompanyAutocompleteProps = {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
}

export function CompanyAutocomplete({ value, onChange, placeholder, className }: CompanyAutocompleteProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [filteredCompanies, setFilteredCompanies] = useState<Company[]>([])
  const wrapperRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleInputChange = (inputValue: string) => {
    onChange(inputValue)

    if (inputValue.trim().length > 0) {
      const filtered = companies.filter((company) => company.name.toLowerCase().includes(inputValue.toLowerCase()))
      setFilteredCompanies(filtered)
      setIsOpen(filtered.length > 0)
    } else {
      setFilteredCompanies([])
      setIsOpen(false)
    }
  }

  const handleSelectCompany = (company: Company) => {
    onChange(company.name)
    setIsOpen(false)
  }

  return (
    <div ref={wrapperRef} className="relative">
      <Input
        value={value}
        onChange={(e) => handleInputChange(e.target.value)}
        onFocus={() => {
          if (value.trim().length > 0 && filteredCompanies.length > 0) {
            setIsOpen(true)
          }
        }}
        placeholder={placeholder}
        className={className}
        autoComplete="off"
      />

      {isOpen && filteredCompanies.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-background border border-border rounded-lg shadow-lg max-h-[300px] overflow-y-auto">
          {filteredCompanies.map((company) => (
            <button
              key={company.id}
              type="button"
              onClick={() => handleSelectCompany(company)}
              className="w-full text-left px-4 py-3 hover:bg-muted transition-colors border-b border-border last:border-b-0 focus:bg-muted focus:outline-none"
            >
              <div className="flex items-start gap-3">
                <Building2 className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-foreground text-sm">{company.name}</p>
                  <div className="flex items-center gap-1 mt-1">
                    <MapPin className="h-3 w-3 text-muted-foreground flex-shrink-0" />
                    <p className="text-xs text-muted-foreground truncate">
                      {company.prefecture} {company.city}
                    </p>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
