from . import db
from flask_login import UserMixin
from . import login_manager


class Host(db.Model):
    """
    表名: host
    id: 业务平台
    platform: 平台
    cluster: 集群名称
    hostname: 主机名称
    device_type: 设备类型
    manufacturer: 设备厂家
    device_model: 设备型号
    serial: 序列号
    account: 账户
    version: 业务版本
    software_version: 软件模块版本号
    local_ip: 内网IP地址
    nat_ip: 映射IP地址
    os_version: 操作系统版本
    engine_room: 所在机房
    frame_number: 机架号
    power_frame_number: 电源柜
    net_time: 入网时间
    period: 过保时间
    status: 状态
    """
    __tablename__ = 'host'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    platform = db.Column(db.String(32), index=True, nullable=False)
    cluster = db.Column(db.String(32), primary_key=True, nullable=False)
    hostname = db.Column(db.String(64), primary_key=True, nullable=False)
    device_type = db.Column(db.String(32), nullable=False)
    manufacturer = db.Column(db.String(32), nullable=True)
    device_model = db.Column(db.String(32), nullable=True)
    serial = db.Column(db.String(32), nullable=True)
    account = db.Column(db.String(32), nullable=True)
    version = db.Column(db.String(64), nullable=True)
    software_version = db.Column(db.String(64), nullable=True)
    local_ip = db.Column(db.String(64), nullable=True)
    nat_ip = db.Column(db.String(64), nullable=True)
    os_version = db.Column(db.String(64), nullable=True)
    engine_room = db.Column(db.String(64), nullable=True)
    frame_number = db.Column(db.String(32), nullable=True)
    power_frame_number = db.Column(db.String(32), nullable=True)
    net_time = db.Column(db.String(32), nullable=True)
    period = db.Column(db.String(32), nullable=True)
    status = db.Column(db.String(32), nullable=True)

    def to_json(self):
        return {
                "id": self.id,
                "platform": self.platform,
                "cluster": self.cluster,
                "hostname": self.hostname,
                "device_type": self.device_type,
                "manufacturer": self.manufacturer,
                "device_model": self.device_model,
                "serial": self.serial,
                "account": self.account,
                "version": self.version,
                "software_version": self.software_version,
                "local_ip": self.local_ip,
                "nat_ip": self.nat_ip,
                "os_version": self.os_version,
                "engine_room": self.engine_room,
                "frame_number": self.frame_number,
                "power_frame_number": self.power_frame_number,
                "net_time": self.net_time,
                "period": self.period,
                "status": self.status
                }


class Capacity(db.Model):
    __tablename__ = 'capacity'
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    platform = db.Column(db.String(32), index=True, nullable=False)
    cluster = db.Column(db.String(32), index=True, unique=True, nullable=False)
    h_capacity = db.Column(db.String(32), nullable=True)
    h_caps = db.Column(db.String(32), nullable=True)
    s_capacity = db.Column(db.String(32), nullable=True)
    s_caps = db.Column(db.String(32), nullable=True)

    def to_json(self):
        return {
            "id": self.id,
            "platform": self.platform,
            "cluster": self.cluster,
            "h_capacity": self.h_capacity,
            "h_caps": self.h_caps,
            "s_capacity": self.s_capacity,
            "s_caps": self.s_caps
        }


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, default=2)

    def verify_password(self, password):
        if password == self.password_hash:
            return True
        else:
            return False

    @property
    def is_admin(self):
        if self.role_id == 1:
            return True
        else:
            return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))