// Layout.js
import React, { useContext, useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ThemeProvider as StyledThemeProvider } from 'styled-components';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faMoon, faSun } from '@fortawesome/free-solid-svg-icons';
import {
  GlobalStyle,
  MainContainer,
  Header, HeaderContent,
  BrandContainer, BrandTitle,
  Nav, NavIcon,
  SearchOverlay, SearchContainer, SearchInput,
  ThemeToggle,
  Footer
} from './MainPage.styles';
import { ThemeContext } from './ThemeContext';
import { lightTheme, darkTheme } from './theme';

export default function Layout({ children }) {
  const { isDark, toggleTheme } = useContext(ThemeContext);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const toggleSearch = () => setIsSearchOpen(o => !o);
  const handleSearchChange = e => setSearchQuery(e.target.value);

  useEffect(() => {
    const onKey = e => e.key === 'Escape' && setIsSearchOpen(false);
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <StyledThemeProvider theme={isDark ? darkTheme : lightTheme}>
      <GlobalStyle />

      <MainContainer>
        <Header>
          <HeaderContent>
            <BrandContainer>
              <BrandTitle>
                <Link to="/main">
                  <span>O</span>ptimal <span>P</span>ick <span>S</span>ystem
                </Link>
              </BrandTitle>
            </BrandContainer>

            <Nav>
              <ul>
                <li>
                  <button
                    type="button"
                    onClick={toggleSearch}
                    style={{ background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    <NavIcon>
                      <FontAwesomeIcon icon={faSearch} />
                    </NavIcon>
                  </button>
                </li>
                <li><Link to="/main">홈</Link></li>
                <li><Link to="/mypage">마이페이지</Link></li>
                <li>
                  <ThemeToggle onClick={toggleTheme}>
                    <FontAwesomeIcon icon={isDark ? faSun : faMoon} />
                  </ThemeToggle>
                </li>
              </ul>
            </Nav>
          </HeaderContent>
        </Header>

        <SearchOverlay isOpen={isSearchOpen} onClick={() => setIsSearchOpen(false)}>
          <SearchContainer onClick={e => e.stopPropagation()}>
            <SearchInput
              type="text"
              placeholder="검색어를 입력하세요..."
              value={searchQuery}
              onChange={handleSearchChange}
              autoFocus
            />
          </SearchContainer>
        </SearchOverlay>

        {/* 여기부터 페이지별 진짜 콘텐츠 */}
        {children}

        <Footer>
          <p>&copy; 2025 Optimal Pick System. All rights reserved.</p>
        </Footer>
      </MainContainer>
    </StyledThemeProvider>
  );
}
