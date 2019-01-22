from flask import render_template, request, jsonify, send_from_directory, redirect
from sqlalchemy import distinct, func, or_
from . import main
from .. import db
from ..models import Host, Capacity
from flask_login import login_required
from ..filesetting import DOWNLOAD_FOLDER


@main.route('/')
@login_required
def index():
    # 按业务平台分类汇总数量
    result = db.session.query(Host.platform, func.count('*').label("count")).filter(Host.status=="在网").group_by(Host.platform).all()
    platforms = [x[0] for x in result]
    platforms_counts = [x[1] for x in result]
    device_nums = sum(platforms_counts)
    # 按机房分类获取数量
    result_jf = db.session.query(Host.engine_room, func.count('*').label("count")).filter(Host.status=="在网").group_by(Host.engine_room).all()
    engine_rooms = [x[0] for x in result_jf]
    engine_rooms_values= [{"value": v, "name": k} for k, v in result_jf]
    # 按设备类型分类获取数量
    result_type = db.session.query(Host.device_type, func.count('*').label("count")).filter(Host.status=="在网").group_by(Host.device_type).all()
    device_types = [x[0] for x in result_type]
    device_types_nums = [x[1] for x in result_type]
    # device_types_values = [{"value": v, "name": k} for k, v in result_type]
    # 统计操作系统
    linux_nums = db.session.query(func.count('*').label("count")).filter(
        or_(Host.os_version.like("linux%"), Host.os_version.like("redhat%"))).all()
    hpux_nums = db.session.query(func.count('*').label("count")).filter(
        or_(Host.os_version.like("HP%"), Host.os_version.like("hp%"))).all()
    aix_nums = db.session.query(func.count('*').label("count")).filter(
        or_(Host.os_version.like("AIX%"), Host.os_version.like("aix%"))).all()
    return render_template('index.html', **locals())


@main.route('/hardware')
@login_required
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
@login_required
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
@login_required
def get_detail():
    temp = ["选择平台", "选择机房", "选择网元", "选择设备类型", "选择操作系统", "选择集群"]
    pt = request.form.get('pt')
    jf = request.form.get('jf')
    jq = request.form.get('jq')
    lx = request.form.get('lx', '')
    zj = request.form.get('zj')
    os_ver = request.form.get('os_ver', '')
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
@login_required
def get_detail_id():
    device_id = request.form.get('id')
    host_info = db.session.query(Host).filter(Host.id == device_id).one()
    result = {
        "flag": "success",
        "hosts": host_info.to_json()
    }
    return jsonify(result)


@main.route('/modify_by_id', methods=["GET", "POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
def capacity():
    show_cols = [('平台', 'platform'), ('集群', 'cluster'), ('硬件容量(W)', 'h_capacity'), ('硬件容量(CAPS)', 'h_caps'),
                 ('软件容量(W)', 's_capacity'), ('软件容量(CAPS)', 's_caps')]
    platforms = db.session.query(distinct(Capacity.platform)).all()
    platform = [x[0] for x in platforms]
    return render_template('capacityInfo.html',show_cols=show_cols, platform=platform)


# 业务容量页面根据选中平台查找对应集群
@main.route('/get_capacity_cluster', methods=["GET", "POST"])
@login_required
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
@login_required
def get_capacity():
    temp = ["选择平台", "选择网元"]
    pt = request.form.get('pt')
    jq = request.form.get('jq')
    kw_temp = {
        "platform": pt if pt and pt not in temp else None,
        "cluster": jq if jq and jq not in temp else None
    }
    kw = {k: v for k, v in kw_temp.items() if v}
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
@login_required
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
@login_required
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
@login_required
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


# 导出查询结果
@main.route('/unload', methods=["GET", "POST"])
@login_required
def unload_excel():
    import pandas, datetime, json, os
    # path = "/Users/EB/PycharmProjects/DeviceManage/unloadfiles/"
    # 清空目录
    try:
        filelist = os.listdir(DOWNLOAD_FOLDER)
        for file in filelist:
            os.remove(DOWNLOAD_FOLDER+file)
    except Exception as e:
        print(str(e))
    temp = request.form.get('data')
    if temp:
        # 需转为json, 不然读取时为字符串
        data_list = json.loads(temp)
        # 最后一列若为修改删除去掉
        datas=[]
        for x in data_list:
            if x[-1]=="操作"or x[-1]=="修改删除":
                datas.append(x[:-1])
            else:
                datas.append(x)
        # datas = [x if "操作" not in x[-1] or "修改" not in  x[-1] else x[:-1] for x in data_list]
        filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".xlsx"
        # 转成pandas  DataFrame格式
        df = pandas.DataFrame(datas[1:], columns=datas[0])
        # 导出excel
        df.to_excel(DOWNLOAD_FOLDER + filename, index=False)
        # 返回生成的excel文件名
        result = {
            "flag": "success",
            "file": filename
        }
    else:
        result = {"flag": "fail",
                  "file": ""}
    return jsonify(result)


# 下载导出的文件
@main.route('/download_file/<filename>')
@login_required
def download_file(filename):
    # path = "/Users/EB/PycharmProjects/DeviceManage/unloadfiles/"
    # file = request.form.get("filename")
    return send_from_directory(DOWNLOAD_FOLDER, filename=filename, as_attachment=True)


@main.route('/search', methods=["GET", "POST"])
@login_required
def search():
    hostname = request.form.get("hostname")
    if hostname:
        search_str = str(hostname) + "%"
        # 按主机名模糊搜索
        search_result = db.session.query(Host).filter(Host.hostname.like(search_str)).all()
        # 获取结果条数
        search_nums = len(search_result)
        return render_template('search.html',search_result=search_result, search_nums=search_nums)
    else:
        return redirect(request.referrer)


# 字段名与数据库表属性映射
value_type_map = {
    "平台": ("platform", Host.platform),
    "网元": ("cluster", Host.cluster),
    "设备类型": ("device_type", Host.device_type),
    "设备型号": ("device_model", Host.device_model),
    "业务版本": ("version", Host.version),
    "软件模块": ("software_version", Host.software_version),
    "操作系统": ("os_version", Host.os_version),
    "机房": ("engine_room", Host.engine_room),
    "状态": ("status", Host.status)
}


# 查询对应类型的数据
def query_by_type(query_type):
    global value_type_map
    query_col = value_type_map.get(query_type, None)
    if query_col:
        cols_temp = db.session.query(distinct(query_col[1])).all()
        cols = [x[0] for x in cols_temp]
    else:
        cols = []
    all_types = list(value_type_map.keys())
    return all_types, cols


@main.route('/custom')
@login_required
def custom():
    # 自定义查询支持的类别
    # value_type = {
    #     "平台": "platform",
    #     "网元": "cluster",
    #     "设备类型": "device_type",
    #     "设备型号": "device_model",
    #     "业务版本": "version",
    #     "软件模块": "software_version",
    #     "操作系统": "os_version",
    #     "机房": "engine_room",
    #     "状态": "status"
    # }
    value_type = {k: v[0] for k, v in value_type_map.items()}
    return render_template('customInfo.html', value_type=value_type)


@main.route('/get_custom_info', methods=["GET", "POST"])
@login_required
def get_custom_info():
    query_type = request.form.get('query_type')
    if query_type != "选择类型一":
        # 获取选中的查询类别
        all_types, cols = query_by_type(query_type)
        # 获取查询类型二，去除已选择的查询类别
        all_types.remove(query_type)
        result = {
            "query_type": query_type,
            "cols": cols,
            "value_type2": all_types
        }
    else:
        result = {
            "query_type": "选择",
            "cols": [],
            "value_type2": []
        }
    return jsonify(result)


# 自定义查询页面查询条件二
@main.route('/get_custom_info2', methods=["GET", "POST"])
@login_required
def get_custom_info2():
    query_type = request.form.get('query_type')
    _, cols = query_by_type(query_type)
    result = {
        "query_type": query_type,
        "cols": cols
    }
    return jsonify(result)


@main.route('/get_custom_detail', methods=["GET", "POST"])
@login_required
def get_custom_detail():
    global value_type_map
    # 获取选择的查询项
    type1 = request.form.get('type1')
    type1_value = request.form.get('type1_value')
    type2 = request.form.get('type2')
    type2_value = request.form.get('type2_value')
    kw = {}
    # 请求参数中有“选择”时，即为未选择查询项，忽略
    for k, v in [(type1, type1_value),(type2, type2_value)]:
        if "选择" not in k and  "选择" not in v:
            kw.update({value_type_map.get(k)[0]: v})
    hosts = db.session.query(Host).filter_by(**kw).all()
    datas = []
    for host in hosts:
        datas.append(host.to_json())
    result = {
        "flag": "success",
        "hosts": datas
    }
    return jsonify(result)