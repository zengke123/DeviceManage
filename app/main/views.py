from flask import render_template, request, jsonify, send_from_directory
from sqlalchemy import distinct
from . import main
from .. import db
from ..models import Host, Capacity


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/hardware')
def hardware():
    # 页面中需显示的列，js中对应列也需要增加
    show_cols = [('平台', 'platform'), ('集群', 'cluster'), ('主机', 'hostname'), ('设备类型', 'device_type'),
                 ('设备厂家', 'manufacturer'), ('设备型号', 'device_model'), ('序列号', 'serial'),
                 ('机房', 'engine_room'), ('机架', 'frame_number'), ('电源柜', 'power_frame_number'),
                 ('入网时间', 'net_time'), ('过保时间', 'period'), ('状态', 'status')]
    platforms = db.session.query(distinct(Host.platform)).all()
    device_types = db.session.query(distinct(Host.device_type)).all()
    platform = [x[0] for x in platforms]
    device_type = [x[0] for x in device_types]
    return render_template('hardwareInfo.html', platform=platform, device_type=device_type, show_cols=show_cols)


@main.route('/get_cluster', methods=["GET", "POST"])
def get_cluster():
    platforms = request.form.get('data')
    clusters = db.session.query(distinct(Host.cluster)).filter(Host.platform == platforms).all()
    rooms = db.session.query(distinct(Host.engine_room)).filter(Host.platform == platforms).all()
    cluster = [x[0] for x in clusters]
    engine_room = [x[0] for x in rooms]
    result = {
        "cluster": cluster,
        "engine_room": engine_room
    }
    return jsonify(result)


@main.route('/get_detail', methods=["GET", "POST"])
def get_detail():
    temp = ["选择平台", "选择机房", "选择网元", "选择设备类型", "选择操作系统", "选择集群"]
    pt = request.form.get('pt')
    jf = request.form.get('jf')
    jq = request.form.get('jq')
    lx = request.form.get('lx','')
    zj = request.form.get('zj')
    os_ver = request.form.get('os_ver','')
    kw_temp = {
        "platform": pt if pt and pt not in temp else None,
        "engine_room": jf if jf and jf not in temp else None,
        "cluster": jq if jq and jq not in temp else None,
        "device_type": lx if lx and lx not in temp else None,
        "hostname": zj if zj and zj not in temp else None,
        "os_version": os_ver if os_ver and os_ver not in temp else None
    }
    kw = {k: v for k, v in kw_temp.items() if v}
    hosts = db.session.query(Host).filter_by(**kw).all()
    datas = []
    for host in hosts:
        datas.append(host.to_json())
    result = {
        "flag": "success",
        "hosts": datas
    }
    return jsonify(result)


@main.route('/get_detail_id', methods=["GET", "POST"])
def get_detail_id():
    device_id = request.form.get('id')
    host_info = db.session.query(Host).filter(Host.id == device_id).one()
    result = {
        "flag": "success",
        "hosts": host_info.to_json()
    }
    return jsonify(result)


@main.route('/modify_by_id', methods=["GET", "POST"])
def modify_by_id():
    datas = request.get_json()
    try:
        device_id = datas.get('id')
        db.session.query(Host).filter(Host.id == device_id).update(datas)
        db.session.commit()
    except Exception as e:
        print(str(e))
    # request中要求的数据格式为json，为其他会导致前端执行success不成功
    result = {"flag": "success"}
    return jsonify(result)


@main.route('/delete_by_id', methods=["GET", "POST"])
def delete_by_id():
    device_id = request.form.get('id')
    try:
        to_delete = Host.query.filter(Host.id == device_id).first()
        db.session.delete(to_delete)
        db.session.commit()
        result = {"flag": "success"}
    except Exception as e:
        print(str(e))
        result = {"flag": "fail"}
    return jsonify(result)


# 软件信息查询页面容量入口
@main.route('/software')
def software():
    show_cols = [('平台', 'platform'), ('集群', 'cluster'), ('主机', 'hostname'), ('账号', 'account'),
                 ('业务版本', 'version'), ('软件模块', 'software_version'), ('操作系统', 'os_version'),
                 ('内网IP', 'local_ip'), ('映射IP', 'nat_ip'), ('状态', 'status')]
    platforms = db.session.query(distinct(Host.platform)).all()
    os_vers = db.session.query(distinct(Host.os_version)).all()
    platform = [x[0] for x in platforms]
    os_ver = [x[0] for x in os_vers]
    return render_template('softwareInfo.html', show_cols=show_cols, platform=platform, os_ver=os_ver)


# 业务系统页面容量入口
@main.route('/capacity')
def capacity():
    show_cols = [('平台', 'platform'), ('集群', 'cluster'), ('硬件容量(W)', 'h_capacity'), ('硬件容量(CAPS)', 'h_caps'),
                 ('软件容量(W)', 's_capacity'), ('软件容量(CAPS)', 's_caps')]
    platforms = db.session.query(distinct(Capacity.platform)).all()
    platform = [x[0] for x in platforms]
    return render_template('capacityInfo.html',show_cols=show_cols, platform=platform)


# 业务容量页面根据选中平台查找对应集群
@main.route('/get_capacity_cluster', methods=["GET", "POST"])
def get_capacity_cluster():
    platforms = request.form.get('data')
    clusters = db.session.query(distinct(Capacity.cluster)).filter(Capacity.platform == platforms).all()
    cluster = [x[0] for x in clusters]
    result = {
        "cluster": cluster
   }
    return jsonify(result)


# 容量页面查询数据
@main.route('/get_capacity', methods=["GET", "POST"])
def get_capacity():
    temp = ["选择平台", "选择网元"]
    pt = request.form.get('pt')
    jq = request.form.get('jq')
    kw_temp = {
        "platform": pt if pt and pt not in temp else None,
        "cluster": jq if jq and jq not in temp else None
    }
    print(kw_temp)
    kw = {k: v for k, v in kw_temp.items() if v}
    print(kw)
    hosts = db.session.query(Capacity).filter_by(**kw).all()
    datas = []
    for host in hosts:
        datas.append(host.to_json())
    result = {
        "flag": "success",
        "hosts": datas
    }
    print(result)
    return jsonify(result)


@main.route('/get_capacity_id', methods=["GET", "POST"])
def get_capacity_id():
    device_id = request.form.get('id')
    info = db.session.query(Capacity).filter(Capacity.id == device_id).one()
    result = {
        "flag": "success",
        "hosts": info.to_json()
    }
    return jsonify(result)


# 容量信息修改提交页面处理函数
@main.route('/modify_capacity_id', methods=["GET", "POST"])
def modify_capacity_id():
    datas = request.get_json()
    try:
        device_id = datas.get('id')
        db.session.query(Capacity).filter(Capacity.id == device_id).update(datas)
        db.session.commit()
    except Exception as e:
        print(str(e))
    # request中要求的数据格式为json，为其他会导致前端执行success不成功
    result = {"flag": "success"}
    return jsonify(result)


# 容量信息删除处理
@main.route('/delete_capacity_id', methods=["GET", "POST"])
def delete_capacity_id():
    device_id = request.form.get('id')
    try:
        to_delete = Capacity.query.filter(Capacity.id == device_id).first()
        db.session.delete(to_delete)
        db.session.commit()
        result = {"flag": "success"}
    except Exception as e:
        print(str(e))
        result = {"flag": "fail"}
    return jsonify(result)


@main.route('/unload', methods=["GET", "POST"])
def unload_excel():
    import pandas, datetime, json, os
    path = "/Users/EB/PycharmProjects/DeviceManage/unloadfiles/"
    try:
        filelist = os.listdir(path)
        print(filelist)
        for file in filelist:
            os.remove(path+file)
    except Exception as e:
        print(str(e))
    temp = request.form.get('data')
    if temp:
        data_list = json.loads(temp)
        datas = [x[:-1] for x in data_list]
        filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx"
        df = pandas.DataFrame(datas[1:], columns=datas[0])
        df.to_excel(path + filename, index=False)
        result = {
            "flag": "success",
            "file": filename
        }
    else:
        result = {"flag": "fail",
                  "file": ""}
    return jsonify(result)


@main.route('/download_file/<filename>')
def download_file(filename):
    path = "/Users/EB/PycharmProjects/DeviceManage/unloadfiles/"
    # file = request.form.get("filename")
    return send_from_directory(path, filename=filename, as_attachment=True)


@main.route('/custom')
def custom():
    return render_template('customInfo.html')