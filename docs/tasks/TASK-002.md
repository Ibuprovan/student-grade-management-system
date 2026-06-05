# TASK-002: 瀛︾敓淇℃伅绠＄悊 API

> **鍒涘缓鏃ユ湡锛?* 2026-06-05  
> **璐熻矗浜猴細** backend-dev  
> **浼樺厛绾э細** P0 (鏍稿績鍔熻兘)  
> **鐘舵€侊細** DONE

---

## 1. 浠诲姟姒傝堪

### 1.1 浠诲姟鎻忚堪

瀹炵幇瀛︾敓淇℃伅绠＄悊鐨勫畬鏁?API 灞傦紝鍖呮嫭 RESTful 鎺ュ彛瀹氫箟銆佷笟鍔￠€昏緫澶勭悊銆佷互鍙?CLI 鍛戒护琛屾帴鍙ｃ€?
### 1.2 涓氬姟鑳屾櫙

鏍规嵁 PRD 鐨勫鐢熶俊鎭鐞嗘ā鍧楋紙F-STD锛夛紝闇€瑕佸疄鐜板鐢熶俊鎭殑澧炲垹鏀规煡鍔熻兘銆侫PI 灞傝礋璐ｆ帴鏀惰姹傘€佽皟鐢?Service 灞傚鐞嗕笟鍔￠€昏緫銆佽繑鍥炲搷搴斻€?
### 1.3 鍏宠仈闇€姹?
| 闇€姹傜紪鍙?| 闇€姹傚悕绉?| 鏉ユ簮鏂囨。 |
|---------|---------|---------|
| F-STD-001 | 娣诲姞瀛︾敓 | prd.md |
| F-STD-002 | 鍒犻櫎瀛︾敓 | prd.md |
| F-STD-003 | 淇敼瀛︾敓 | prd.md |
| F-STD-004 | 鏌ヨ瀛︾敓 | prd.md |
| F-STD-005 | 瀛︾敓鍒楄〃 | prd.md |

---

## 2. 璇︾粏浠诲姟娓呭崟

### 2.1 涓氬姟閫昏緫灞傦紙services/锛?
| 搴忓彿 | 瀛愪换鍔?| 鏂囦欢璺緞 | 璇存槑 | 鐘舵€?|
|-----|--------|---------|------|------|
| 1.1 | 鍒涘缓 StudentService | `src/services/student_service.py` | 瀛︾敓涓氬姟閫昏緫锛氬鍒犳敼鏌ャ€佸鍙峰敮涓€鎬ф牎楠?| TODO |

### 2.2 API 璺敱灞傦紙api/routes/锛?
| 搴忓彿 | 瀛愪换鍔?| 鏂囦欢璺緞 | 璇存槑 | 鐘舵€?|
|-----|--------|---------|------|------|
| 2.1 | 鍒涘缓瀛︾敓 API 璺敱 | `src/api/routes/students.py` | RESTful 鎺ュ彛锛歅OST/GET/PUT/DELETE | TODO |
| 2.2 | 鍒涘缓渚濊禆娉ㄥ叆 | `src/api/dependencies.py` | 鏁版嵁搴撲細璇濄€丼ervice 瀹炰緥娉ㄥ叆 | TODO |

### 2.3 CLI 鍛戒护灞傦紙cli/锛?
| 搴忓彿 | 瀛愪换鍔?| 鏂囦欢璺緞 | 璇存槑 | 鐘舵€?|
|-----|--------|---------|------|------|
| 3.1 | 鍒涘缓瀛︾敓 CLI 鍛戒护 | `src/cli/commands/student_cmd.py` | 鍛戒护琛屾帴鍙ｏ細add, list, search, update, delete | TODO |

### 2.4 寮傚父澶勭悊

| 搴忓彿 | 瀛愪换鍔?| 鏂囦欢璺緞 | 璇存槑 | 鐘舵€?|
|-----|--------|---------|------|------|
| 4.1 | 鍒涘缓寮傚父澶勭悊鍣?| `src/api/exception_handlers.py` | 鍏ㄥ眬寮傚父澶勭悊锛岀粺涓€閿欒鍝嶅簲鏍煎紡 | TODO |

---

## 3. API 鎺ュ彛瑙勮寖

### 3.1 鎺ュ彛鍒楄〃

| 鏂规硶 | 璺緞 | 鍔熻兘 | 璇锋眰鍙傛暟 | 鍝嶅簲鏍煎紡 |
|------|------|------|---------|---------|
| POST | `/api/students` | 娣诲姞瀛︾敓 | StudentCreate | StudentResponse |
| GET | `/api/students/{student_id}` | 鏌ヨ瀛︾敓 | student_id | StudentResponse |
| GET | `/api/students` | 瀛︾敓鍒楄〃 | page, page_size, class_name | List[StudentResponse] |
| PUT | `/api/students/{student_id}` | 淇敼瀛︾敓 | StudentUpdate | StudentResponse |
| DELETE | `/api/students/{student_id}` | 鍒犻櫎瀛︾敓 | student_id | SuccessResponse |
| GET | `/api/students/search` | 鎼滅储瀛︾敓 | keyword, class_name | List[StudentResponse] |

### 3.2 璇锋眰/鍝嶅簲鏍煎紡

#### 娣诲姞瀛︾敓 (POST /api/students)

**璇锋眰浣擄細**
```json
{
    "student_id": "20260001",
    "name": "寮犱笁",
    "gender": "鐢?,
    "class_name": "涓夊勾涓€鐝?,
    "enrollment_year": 2026
}
```

**鎴愬姛鍝嶅簲 (201)锛?*
```json
{
    "success": true,
    "data": {
        "student_id": "20260001",
        "name": "寮犱笁",
        "gender": "鐢?,
        "class_name": "涓夊勾涓€鐝?,
        "enrollment_year": 2026,
        "created_at": "2026-06-05T10:00:00",
        "updated_at": "2026-06-05T10:00:00"
    }
}
```

**閿欒鍝嶅簲 (409)锛?*
```json
{
    "success": false,
    "error": {
        "code": "DUPLICATE",
        "message": "瀛︾敓 鐨?瀛﹀彿 '20260001' 宸插瓨鍦?
    }
}
```

#### 瀛︾敓鍒楄〃 (GET /api/students)

**鏌ヨ鍙傛暟锛?*
- `page`: 椤电爜锛堥粯璁?1锛?- `page_size`: 姣忛〉鏁伴噺锛堥粯璁?20锛屾渶澶?100锛?- `class_name`: 鐝骇绛涢€夛紙鍙€夛級

**鎴愬姛鍝嶅簲 (200)锛?*
```json
{
    "success": true,
    "data": {
        "items": [
            {
                "student_id": "20260001",
                "name": "寮犱笁",
                "gender": "鐢?,
                "class_name": "涓夊勾涓€鐝?,
                "enrollment_year": 2026
            }
        ],
        "total": 100,
        "page": 1,
        "page_size": 20
    }
}
```

### 3.3 CLI 鍛戒护瑙勮寖

```bash
# 娣诲姞瀛︾敓
python -m src.cli student add --id 20260001 --name 寮犱笁 --gender 鐢?--class 涓夊勾涓€鐝?--year 2026

# 瀛︾敓鍒楄〃
python -m src.cli student list [--class 涓夊勾涓€鐝璢 [--page 1] [--size 20]

# 鎼滅储瀛︾敓
python -m src.cli student search --keyword 寮犱笁

# 淇敼瀛︾敓
python -m src.cli student update --id 20260001 --name 鏉庡洓

# 鍒犻櫎瀛︾敓
python -m src.cli student delete --id 20260001
```

---

## 4. 涓氬姟閫昏緫瑙勮寖

### 4.1 娣诲姞瀛︾敓娴佺▼

```
1. 鎺ユ敹璇锋眰鏁版嵁
2. Pydantic 楠岃瘉鏁版嵁鏍煎紡
3. 妫€鏌ュ鍙锋槸鍚﹀凡瀛樺湪
   - 瀛樺湪 鈫?杩斿洖 409 閿欒
   - 涓嶅瓨鍦?鈫?缁х画
4. 鍒涘缓瀛︾敓璁板綍
5. 杩斿洖鍒涘缓鎴愬姛鍝嶅簲
```

### 4.2 鏌ヨ瀛︾敓娴佺▼

```
1. 鎺ユ敹鏌ヨ鍙傛暟
2. 鏋勫缓鏌ヨ鏉′欢
   - 鎸夊鍙锋煡璇細绮剧‘鍖归厤
   - 鎸夊鍚嶆煡璇細妯＄硦鍖归厤
   - 鎸夌彮绾ф煡璇細绮剧‘鍖归厤
3. 鎵ц鍒嗛〉鏌ヨ
4. 杩斿洖瀛︾敓鍒楄〃
```

### 4.3 涓氬姟瑙勫垯

| 瑙勫垯缂栧彿 | 瑙勫垯鎻忚堪 | 瀹炵幇浣嶇疆 |
|---------|---------|---------|
| BR-STD-001 | 瀛﹀彿蹇呴』鍞竴 | StudentService.create_student() |
| BR-STD-002 | 瀛﹀彿鏍煎紡楠岃瘉锛?浣嶆暟瀛楋級 | StudentSchema.validator |
| BR-STD-003 | 濮撳悕闀垮害 2-20 瀛楃 | StudentSchema.Field |
| BR-STD-004 | 鍒犻櫎瀛︾敓鏃剁骇鑱斿垹闄ゆ垚缁?| Student 妯″瀷 cascade 璁剧疆 |

---

## 5. 楠屾敹鏍囧噯

### 5.1 鍔熻兘楠屾敹

| 楠屾敹椤?| 楠屾敹鏍囧噯 | 娴嬭瘯鏂规硶 |
|-------|---------|---------|
| 娣诲姞瀛︾敓 | 鎴愬姛鍒涘缓瀛︾敓璁板綍锛岃繑鍥炲畬鏁翠俊鎭?| API 娴嬭瘯 |
| 瀛﹀彿閲嶅 | 杩斿洖 409 閿欒锛屾彁绀哄鍙峰凡瀛樺湪 | API 娴嬭瘯 |
| 鏌ヨ瀛︾敓 | 鎸夊鍙?濮撳悕/鐝骇姝ｇ‘鏌ヨ | API 娴嬭瘯 |
| 瀛︾敓鍒楄〃 | 鍒嗛〉鏌ヨ姝ｇ‘锛屾敮鎸佺彮绾х瓫閫?| API 娴嬭瘯 |
| 淇敼瀛︾敓 | 鎴愬姛鏇存柊瀛︾敓淇℃伅 | API 娴嬭瘯 |
| 鍒犻櫎瀛︾敓 | 鎴愬姛鍒犻櫎瀛︾敓锛岀骇鑱斿垹闄ゆ垚缁?| API 娴嬭瘯 |
| CLI 鍛戒护 | 鎵€鏈?CLI 鍛戒护姝ｅ父宸ヤ綔 | 闆嗘垚娴嬭瘯 |

### 5.2 鎬ц兘楠屾敹

| 楠屾敹椤?| 楠屾敹鏍囧噯 | 娴嬭瘯鏂规硶 |
|-------|---------|---------|
| 鍗曟潯鏌ヨ | 鍝嶅簲鏃堕棿 < 10ms | 鎬ц兘娴嬭瘯 |
| 鍒楄〃鏌ヨ | 10000 鏉℃暟鎹搷搴?< 100ms | 鍘嬪姏娴嬭瘯 |

---

## 6. 渚濊禆鍏崇郴

### 6.1 鍓嶇疆渚濊禆

| 浠诲姟缂栧彿 | 浠诲姟鍚嶇О | 渚濊禆璇存槑 |
|---------|---------|---------|
| TASK-001 | 鏁版嵁搴撴ā鍨嬪疄鐜?| 渚濊禆 Student 妯″瀷銆丷epository銆丼chema |

### 6.2 鍚庣画渚濊禆

鏃?
---

## 7. 椋庨櫓涓庢敞鎰忎簨椤?
| 椋庨櫓椤?| 璇存槑 | 搴斿鎺柦 |
|-------|------|---------|
| 瀛﹀彿鍐茬獊 | 骞跺彂娣诲姞鐩稿悓瀛﹀彿 | 鏁版嵁搴撳敮涓€绾︽潫 + 涓氬姟灞傛牎楠?|
| 澶ч噺鏁版嵁鏌ヨ | 瀛︾敓鏁伴噺澶氭椂鏌ヨ鎱?| 鍒嗛〉鏌ヨ + 绱㈠紩浼樺寲 |
| 绾ц仈鍒犻櫎 | 鍒犻櫎瀛︾敓鏃舵垚缁╂暟鎹涪澶?| 纭涓氬姟闇€姹傦紝娣诲姞纭鎻愮ず |

---

## 8. 宸ヤ綔閲忎及绠?
| 瀛愪换鍔?| 棰勪及宸ユ椂 | 澶囨敞 |
|--------|---------|------|
| StudentService | 3h | 涓氬姟閫昏緫瀹炵幇 |
| API 璺敱 | 2h | RESTful 鎺ュ彛 |
| CLI 鍛戒护 | 2h | 鍛戒护琛屾帴鍙?|
| 寮傚父澶勭悊 | 1h | 鍏ㄥ眬寮傚父澶勭悊鍣?|
| 鍗曞厓娴嬭瘯 | 3h | 娴嬭瘯鐢ㄤ緥缂栧啓 |
| **鍚堣** | **11h** | |

---

## 9. 杈撳嚭鐗╂竻鍗?
- [ ] `src/services/student_service.py` - 瀛︾敓涓氬姟閫昏緫
- [ ] `src/api/routes/students.py` - 瀛︾敓 API 璺敱
- [ ] `src/api/dependencies.py` - 渚濊禆娉ㄥ叆閰嶇疆
- [ ] `src/api/exception_handlers.py` - 鍏ㄥ眬寮傚父澶勭悊
- [ ] `src/cli/commands/student_cmd.py` - 瀛︾敓 CLI 鍛戒护
- [ ] `tests/unit/test_services/test_student_service.py` - Service 鍗曞厓娴嬭瘯
- [ ] `tests/integration/test_api/test_students.py` - API 闆嗘垚娴嬭瘯

---

> **浠诲姟鐘舵€佸彉鏇磋褰?*
> 
> | 鏃堕棿 | 鐘舵€佸彉鏇?| 鎿嶄綔浜?| 澶囨敞 |
> |------|---------|--------|------|
> | 2026-06-05 | - 鈫?TODO | PMO | 浠诲姟鍒涘缓 |





