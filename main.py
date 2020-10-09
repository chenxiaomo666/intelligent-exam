from intelligent_exam import app


def main():
    app.run(host='0.0.0.0', port='9990', debug=False, ssl_context=("./cert/4075081_dev.mylwx.cn.pem", "./cert/4075081_dev.mylwx.cn.key"))

if __name__ == "__main__":
    main()
