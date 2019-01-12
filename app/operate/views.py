from . import operate
from .. import db
from ..models import Host, Capacity
from flask import render_template, request, jsonify


@operate.route('/new')
def new():
    show_cols_h = [('* 平台', 'platform'), ('* 集群', 'cluster'), ('* 主机', 'hostname'),
                   ('设备类型', 'device_type'), ('设备厂家', 'manufacturer'), ('设备型号', 'device_model'),
                   ('序列号', 'serial'), ('账户', 'account'),('业务版本', 'version'),('软件模块', 'software_version'),
                   ('内网IP', 'local_ip'),('映射IP', 'nat_ip'),('操作系统', 'os_version'),
                   ('机房', 'engine_room'), ('机架', 'frame_number'), ('电源柜', 'power_frame_number'),
                   ('入网时间', 'net_time'), ('过保时间', 'period'), ('状态', 'status')]
    show_cols_s = [('* 平台', 'platform'), ('* 集群', 'cluster'), ('硬件容量(W)', 'h_capacity'),
                   ('硬件容量(CAPS)', 'h_caps'), ('软件容量(W)', 's_capacity'), ('软件容量(CAPS)', 's_caps')]
    return render_template("new_device.html", show_cols_h=show_cols_h, show_cols_s=show_cols_s)


@operate.route('/add_new', methods=["GET", "POST"])
def add_new():
    datas = request.get_json()
    try:
        add_host = Host(**datas)
        db.session.add(add_host)
        db.session.commit()
        result = {"flag": "success"}
    except Exception as e:
        print(str(e))
        result = {"flag": "fail"}
    return jsonify(result)


@operate.route('/add_new_s', methods=["GET", "POST"])
def add_new_s():
    datas = request.get_json()
    try:
        add_host = Capacity(**datas)
        db.session.add(add_host)
        db.session.commit()
        result = {"flag": "success"}
    except Exception as e:
        print(str(e))
        result = {"flag": "fail"}
    return jsonify(result)


@operate.route('/load')
def load():
    return render_template("load_device.html")


