def qs_checker(qs_dict):
    if any(len(v) < 5 for v in qs_dict.values()):
        replacement_list = [k for k, v in qs_dict.items() if len(v) < 5]
        for replacement_key in replacement_list:
            if 'BOS' in replacement_key:
                qs_dict.update({replacement_key: qs_dict['BOS_qs1']})
            elif 'OPP' in replacement_key:
                qs_dict.update({replacement_key: qs_dict['OPP_qs1']})
    else:
        pass
