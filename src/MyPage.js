import React from 'react';
import Layout from './Layout';
import styled from 'styled-components';

// 페이지별 추가 스타일만 정의
const UserInfo = styled.div`
  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
  }
  .info-item {
    label {
      font-weight: bold;
      display: block;
      margin-bottom: 8px;
    }
    p {
      margin: 0;
    }
  }
`;

export default function MyPage() {
  return (
    <Layout>
      <div className="mypage-content">
        <h2>마이페이지</h2>

        <UserInfo id="user-info">
          <h3>개인정보</h3>
          <div className="info-grid">
            <div className="info-item">
              <label>이름</label>
              <p>홍길동</p>
            </div>
            <div className="info-item">
              <label>아이디</label>
              <p>hong123</p>
            </div>
            <div className="info-item">
              <label>생년월일</label>
              <p>1990-01-01</p>
            </div>
            <div className="info-item">
              <label>이메일</label>
              <p>hong123@email.com</p>
            </div>
            <div className="info-item">
              <label>연락처</label>
              <p>010-1234-5678</p>
            </div>
          </div>
        </UserInfo>
      </div>
    </Layout>
  );
}
