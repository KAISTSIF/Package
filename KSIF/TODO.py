"""
   =========
   TODO List
   =========

   Project의 의의
   --------------
      1. 장점 : 다른 사람이 만들어놓은 Module를 간단하게 사용, 응용 가능 (매우 빠르게).
                다양한 코딩 테크닉 배울 수 있음.
                저장, 배포, 관리가 용이함.
                특히나 Python은 다양한 Platform Implementation이 가능 + 최신 Algorithm Package 도입 가능.
                사회에 나가서도 업데이트 된 KSIF Package를 사용할 수 있음.
                필요하다면 Security를 강화해서 Public에 공개되는 것을 막을 수 있음.

      2. 요약 : Versatility
                Integrability
                Easy Management
                Easy Implementation

      3. 외부 패키지 안 쓰는 이유 : backtest는 외부 package 쓸 만큼 어려운 작업이 아님
                                    전략에 따라서 사용자가 코드를 많이 바꿔야함
                                    다양한 기능을 implement 해야하고 이를 사용자가 쉽게 사용해야함.

    Project의 이론적 기반
    ---------------------

       1. Strategic Algebra::

          전략의 연산 체계가 필요함
          (e.g. 운용3팀 전략이 AI팀 전략과 correlation 없게 할 때,
                전략에서 고른 종목 빼고 나머지의 성능을 알고 싶을 때,
                전략들을 겹치고 싶을 때)

           (+) 종목들의 Union
           (*) 종목들의 Intersection

           Strategy는 portfolio weight vector를 return 하는 함수수

          => Associative, Commuatative => Vector Space.

   필요한 Modules
   --------------

     1. Python MySQL 연동 Module : For Constructing DataBase. (창희, 필요한 사항이 뭔지 구체적으로 팀별로 말하기)
     2. Raw Data Manipulation Module : For SAS-free Framework. (창희)
     3. Bloomberg Python API 연동 Module : For Real-Time Data Acquisition. (창희, 김행란 선생님께 블룸버그 API 제공하는 버전 쓰는지 물어보기, 더 비싼 버전인지)
     4. 한국투자증권 API 연동 (C++) Module : For Algorithmic Trading. (세준)
     5. Text Mining Module : For News, Consensus, Reports Data Acquisition, Find NEWS wire Services. (세준)
     6. Technical Analysis Module : For getting Technical indicators like MACD, Bollinger Band. (동욱)
     7. Machine Learning Module : For Training Strategies using like PCA(창희), Gaussian Process(승현 도움), Neural Networks.(창희), SVM(창희),
     8. Visualization Module : For visualize raw data, backtest results. (도결)


   기타 필요한 사항
   ----------------

      1. GitHub에 버전별로 올려서 관리하기. (비공개로 하러면 유료)
      2. Cross-Platform 가능하도록 설계 (SAS, Matlab, Mathematica, C++, R 등 사용가능하도록).
      3. 실제 증권사에 가서 데이터는 어떻게 받고, DataBase는 어떻게 구축하고, 백테스팅 플랫폼은.
         어떻게 만들었는지 묻기 +\alpha 해외 Hedge Funds는 어떻게 전산시스템 구축하는지 Research (Like WorldQuant).
      4. Pandas 에서 SAS SQL 처럼 효율적으로 conditional merge 하는 방법 찾기.
      5. Pandas 에서 Lag 함수를 이용해 Conditional Operation 하는 방법 찾기.


   필요한 Data Structures
   ----------------------

      1. Stock Price, News, 기업 공시 등은 Continuous Data.
      2. Financial Statements는 Quarterly Data이므로 위와 구별하여 데이터를 만들것.
      3. 1,2를 합하여 variables를 만들고 최종 데이터베이스로 저장.

   기타
   ----


"""