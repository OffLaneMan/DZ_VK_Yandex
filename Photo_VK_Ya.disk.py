from sys import exception
import requests
import datetime
import json
import os


token_yandex = ""
access_token = ""
id = ""


class VK:
    """Класс VK нужно ввести access_token и id"""

    def __init__(self, access_token, id, version="5.131"):
        self.__token = access_token
        self.__version = version
        self.__id = id
        self.__params = {"access_token": self.__token, "v": self.__version}

    def __metod(self, metod):
        """метод"""
        return f"https://api.vk.com/method/{metod}"

    def photo_profile(self, count=5):
        """Получение JSON профиля"""
        response = requests.get(
            self.__metod("photos.get"),
            params={
                **self.__params,
                "owner_id": self.__id,
                "album_id": "profile",
                "extended": 1,
            },
        )
        if 200 <= response.status_code < 300:
            return self.__dict_photo(response.json(), count)
        else:
            print("не получилось установить связь")

    def __dict_photo(self, js, count):
        """удалить лишние данные из JSON, оставить count данных от новых к старым"""
        js_url_likes_date = []
        for i in js["response"]["items"][-1 : -count - 1 : -1]:
            js_url_likes_date.append(
                {
                    "date": datetime.datetime.fromtimestamp(i["date"]).strftime(
                        "%d.%m.%Y %H:%M:%S"
                    ),
                    "likes": i["likes"]["count"],
                    "url": i["sizes"][-1]["url"],
                    "size": i["sizes"][-1]["type"],
                }
            )
        return js_url_likes_date


class Yandex:
    """Класс яндекс, нужно ввести токен"""

    def __init__(self, token_yandex):
        self.__headers = {"Authorization": token_yandex}
        self.__folder = False

    def __create_folder(self, path):
        """Создать папку"""
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        response = requests.put(url, params={"path": path}, headers=self.__headers)
        if response.status_code == 201:
            self.__folder = True
            print("папка успешно создана на яндекс диске")
        elif response.status_code == 409:
            self.__folder = True
            print("папка уже существует на яндекс диске")
        else:
            print("не получилось создать папку на яндекс диске")

    def __request_URL_for_download(self, path, file):
        """Получить ссылку для загрузги файла"""
        if self.__folder != True:
            self.__create_folder(path)
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        response = requests.get(
            url, headers=self.__headers, params={"path": path + "/" + file}
        )
        if 200 == response.status_code:
            return response.json()["href"]
        else:
            print("не получилось загрузить файл на яндекс диск")

    def __dowload_file_yandex_disk(self, url, file, path="Папка с фотографиями из ВК"):
        """Загрузить файл в папку"""
        url_dowload = self.__request_URL_for_download(path, file)
        if url_dowload is not None:
            response2 = requests.get(url)
            response = requests.put(url_dowload, files={"file": response2.content})
            if response.status_code == 201:
                print("файл успешно загрузился на яндекс диск")
                return "ok"
            elif response.status_code == 202:
                print(
                    "файл принят сервером, но еще не был перенесен непосредственно в яндекс диск"
                )
                return "ok"
            else:
                print("файл не был загружен на яндекс диск")

    def dowload_file_from_vk(self, vk, count=5, path="Папка с фотографиями из ВК"):
        if isinstance(vk, VK):
            js = []
            photo = vk.photo_profile(count)
            like = [x["likes"] for x in photo]
            for i in range(count):
                if like.count(photo[i]["likes"]) >= 2:
                    v = self.__dowload_file_yandex_disk(
                        photo[i]["url"],
                        f'{photo[i]["likes"]} {photo[i]["date"]}.jpg',
                        path,
                    )
                    if v == "ok":
                        js.append(
                            {
                                "file_name": f'{photo[i]["likes"]} {photo[i]["date"]}.jpg',
                                "size": photo[i]["size"],
                            }
                        )
                else:
                    v = self.__dowload_file_yandex_disk(
                        photo[i]["url"],
                        f'{photo[i]["likes"]}.jpg',
                        path,
                    )
                    if v == "ok":
                        js.append(
                            {
                                "file_name": f'{photo[i]["likes"]}.jpg',
                                "size": photo[i]["size"],
                            }
                        )
            if js:
                self.__dump_json(js)
        else:
            print("первый параметр функции должен принадлежать к Классу VK")

    def __dump_json(self, js, name_file="json-файл"):
        with open(
            os.path.join(os.path.dirname(__file__), f"{name_file}.json"), "w"
        ) as f:
            json.dump(js, f, ensure_ascii=False, indent=2)
            print(f"json-файл с именем {name_file}.json записан")


if __name__ == "__main__":
    class_vk1 = VK(access_token, id)
    class_yandex = Yandex(token_yandex)
    try:
        class_yandex.dowload_file_from_vk(class_vk1)
    except Exception as e:
        print("Произошла ошибка в выполнении кода")
