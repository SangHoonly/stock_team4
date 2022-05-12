## 실시간 주가 현황 확인 어플리케이션

E반 4조의 첫번째 프로젝트!


### [Notion 링크](https://right-gargoyle-320.notion.site/99-1-4-a1b219c53df64a65a6b4a7c110446319)


### Description

- 비회원이 메인페이지를 접근하면 상위 4개의 주식 종류가 보인다.
- 회원이 메인페이지를 접근하면 자신이 등록한 주식목록과 관심있는 주식을 등록할 수 있다.

### Environment

- AWS EC2 (Ubuntu)


### Project Tree📂
```
 📦aop
 ┗ 📜Aop.py
 📦config
 ┗ 📜config.py
 📦model
 ┣ 📜favoriteDao.py
 ┣ 📜stockDao.py
 ┗ 📜userDao.py
📦scripts
 ┗ 📜deploy.sh
📦service
 ┣ 📜FavoriteService.py
 ┣ 📜service.py
 ┣ 📜StockService.py
 ┗ 📜UserService.py
📦static
 ┣ 📜company_list.json
 ┗ 📜usermain_header.jpg 
📦templates
 ┣ 📜index.html
 ┣ 📜index2.html
 ┣ 📜login.html
 ┣ 📜my_page.html
 ┣ 📜sign_up.html
 ┗ 📜user_main.html
📦view
 ┗ 📜view.py
 📜app.py
```
###  __Stacks__ 📚


#### Server 
<img src="https://img.shields.io/badge/Amazon%20EC2-232F3E?style=for-the-badge&logo=Amazon%20AWS&logoColor=white]"/>

#### Framework
<img src="https://img.shields.io/badge/flask-000000?style=for-the-badge&logo=FLASK&logoColor=white"/>

#### Language
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=Jinja&logoColor=white]"/>

#### Database
<img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=MongoDB&logoColor=white"/>

#### View
<img src="https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=CSS3&logoColor=white"/><img src="https://img.shields.io/badge/HTML-E34F26?style=for-the-badge&logo=HTML5&logoColor=white"/><img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=white"/><img src="https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jQuery&logoColor=white"/>

#### Tool
<img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white]"/><img src="https://img.shields.io/badge/Git-00000?style=for-the-badge&logo=Git&logoColor=F05032]"/><img src="https://img.shields.io/badge/Github-181717?style=for-the-badge&logo=Github&logoColor=white]"/><img src="https://img.shields.io/badge/Sourcetree-0052CC?style=for-the-badge&logo=Sourcetree&logoColor=white]"/>
