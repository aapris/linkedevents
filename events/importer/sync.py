class ModelSyncher(object):
    def __init__(self, queryset, generate_obj_id, delete_func=None, check_deleted_func=None):
        d = {}
        self.generate_obj_id = generate_obj_id
        self.delete_func = delete_func
        self.check_deleted_func = check_deleted_func
        # Generate a list of all objects
        for obj in queryset:
            d[generate_obj_id(obj)] = obj
            obj._found = False
            obj._changed = False

        self.obj_dict = d

    def mark(self, obj):
        if getattr(obj, '_found', False):
            raise Exception("Object %s already marked" % obj)

        obj_id = self.generate_obj_id(obj)
        if obj_id not in self.obj_dict:
            self.obj_dict[obj_id] = obj
        else:
            obj = self.obj_dict[obj_id]
        obj._found = True

    def get(self, obj_id):
        return self.obj_dict.get(obj_id, None)

    def finish(self):
        delete_list = []
        for obj_id, obj in self.obj_dict.items():
            if obj._found:
                continue
            if self.check_deleted_func is not None and self.check_deleted_func(obj):
                continue
            delete_list.append(obj)
        if len(delete_list) > 5 and len(delete_list) > len(self.obj_dict) * 0.2:
            raise Exception("Attempting to delete more than 20% of total items")
        for obj in delete_list:
            if self.delete_func:
                deleted = self.delete_func(obj)
            else:
                obj.delete()
                deleted = True
            if deleted:
                print("Deleting object %s" % obj)
