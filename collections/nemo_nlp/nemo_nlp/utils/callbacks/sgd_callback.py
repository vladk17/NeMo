# Copyright (c) 2019 NVIDIA Corporation
__all__ = ['eval_iter_callback', 'eval_epochs_done_callback']

import collections
import numpy as np
import torch

from nemo.utils.exp_logging import get_logger
import nemo_nlp
from nemo_nlp.utils.metrics.sgd_metrics import *

logger = get_logger('')


def eval_iter_callback(tensors,
                       global_vars):

    if 'logit_intent_status' not in global_vars:
        global_vars['logit_intent_status'] = []
    if 'logit_req_slot_status' not in global_vars:
        global_vars['logit_req_slot_status'] = []
    if 'logit_cat_slot_status' not in global_vars:
        global_vars['logit_cat_slot_status'] = []
    if 'logit_cat_slot_value' not in global_vars:
        global_vars['logit_cat_slot_value'] = []
    
    if 'logit_noncat_slot_status' not in global_vars:
        global_vars['logit_noncat_slot_status'] = []
    if 'logit_noncat_slot_start' not in global_vars:
        global_vars['logit_noncat_slot_start'] = []
    if 'logit_noncat_slot_end' not in global_vars:
        global_vars['logit_noncat_slot_end'] = []

    if 'intent_status' not in global_vars:
        global_vars['intent_status'] = []
    if 'requested_slot_status' not in global_vars:
        global_vars['requested_slot_status'] = []
    if 'intent_status' not in global_vars:
        global_vars['intent_status'] = []

    if 'num_slots' not in global_vars:
        global_vars['num_slots'] = []
    if 'categorical_slot_status' not in global_vars:
        global_vars['categorical_slot_status'] = []
    if 'num_categorical_slots' not in global_vars:
        global_vars['num_categorical_slots'] = []
    if 'categorical_slot_values' not in global_vars:
        global_vars['categorical_slot_values'] = []
    if 'noncategorical_slot_status' not in global_vars:
        global_vars['noncategorical_slot_status'] = []
    if 'categorical_slot_values' not in global_vars:
        global_vars['categorical_slot_values'] = []
    if 'num_noncategorical_slots' not in global_vars:
        global_vars['num_noncategorical_slots'] = []
    if 'noncategorical_slot_value_start' not in global_vars:
        global_vars['noncategorical_slot_value_start'] = []
    if 'noncategorical_slot_value_end' not in global_vars:
        global_vars['noncategorical_slot_value_end'] = []


    for kv, v in tensors.items():
        # intents
        if kv.startswith('logit_intent_status'):
            logit_intent_status = v[0]
        elif kv.startswith('intent_status'):
            intent_status = v[0]

        # noncategorical slots
        elif kv.startswith('logit_noncat_slot_status'):
            logit_noncat_slot_status = v[0]
        elif kv.startswith('logit_noncat_slot_start'):
            logit_noncat_slot_start = v[0]
        elif kv.startswith('logit_noncat_slot_end'):
            logit_noncat_slot_end = v[0]
        elif kv.startswith('noncategorical_slot_status'):
            noncategorical_slot_status = v[0]
        elif kv.startswith('num_noncategorical_slots'):
            num_noncategorical_slots = v[0]
        elif kv.startswith('noncategorical_slot_value_start'):
            noncategorical_slot_value_start = v[0]
        elif kv.startswith('noncategorical_slot_value_end'):
            noncategorical_slot_value_end = v[0]

        # requested slots
        elif kv.startswith('logit_req_slot_status'):
            logit_req_slot_status = v[0]
        elif kv.startswith('requested_slot_status'):
            requested_slot_status = v[0]

        elif kv.startswith('logit_cat_slot_status'):
            global_vars['logit_cat_slot_status'].append(v[0].cpu().numpy())
        elif kv.startswith('logit_cat_slot_value'):
            global_vars['logit_cat_slot_value'].append(v[0].cpu().numpy())
        

        
        elif kv.startswith('num_slots'):
            global_vars['num_slots'].append(v[0].cpu().numpy())
        elif kv.startswith('categorical_slot_status'):
            global_vars['categorical_slot_status'].append(v[0].cpu().numpy())
        elif kv.startswith('num_categorical_slots'):
            global_vars['num_categorical_slots'].append(v[0].cpu().numpy())
        elif kv.startswith('categorical_slot_values'):
            global_vars['categorical_slot_values'].append(v[0].cpu().numpy())
        

        

    import pdb; pdb.set_trace()

    num_active_intents = torch.sum(intent_status, axis=1).unsqueeze(1)

    # the intents represented as a one hot vectors
    # logits shape [batch, max_num_intents + 1] where 1 is for NONE intent

    active_intent_onehot_labels = intent_status[num_active_intents.view(-1) > 0.5]
    # get indices of active intents and add 1 to take into account NONE intent
    active_intent_labels = active_intent_onehot_labels.max(dim=1)[1] + 1

    active_intent_preds = torch.argmax(logit_intent_status, 1)[num_active_intents.view(-1) > 0.5]

    global_vars['active_intent_labels'].extend(actieve_intent_labels.cpu().numpy())
    global_vars['active_intent_preds'].extend(active_intent_preds.cpu().numpy())

    import pdb; pdb.set_trace()

    '''
    num_active_intents = torch.sum(intent_status, axis=1).unsqueeze(1)
    tensor_ones = torch.ones(num_active_intents.size(), dtype=torch.long)
 
    if num_active_intents.is_cuda:
        tensor_ones = tensor_ones.cuda()
 
    # adding label for NONE intent - 1 if no acive intent for the dialogue
    none_intent_label = tensor_ones - num_active_intents
    onehot_intent_labels = torch.cat([none_intent_label, intent_status], axis=1)
    _, intent_labels = onehot_intent_labels.max(dim=1)

    '''

    # mask example with no noncategorical slots
    noncat_slots_mask = torch.sum(noncategorical_slot_status, 1) > 0

    # mask examples with no
    torch.sum(requested_slot_status, -1) > 0


    # point_outputs_max = torch.argmax(point_outputs, dim=-1)
    # mask_paddings = (tgt_ids == data_desc.vocab.pad_id)
    # comp_res = ((point_outputs_max == tgt_ids) | mask_paddings)
    # comp_res = torch.all(comp_res, axis=-1, keepdims=False)

    # global_vars['comp_res'].extend(comp_res.cpu().numpy())
    # global_vars['gating_preds'].extend(torch.argmax(gate_outputs, axis=-1).cpu().numpy())


def eval_epochs_done_callback(global_vars):
    active_intent_labels = np.asarray(global_vars['active_intent_labels'])
    active_intent_status_preds = np.asarray(global_vars['active_intent_preds'])

    active_intent_accuracy = sum(active_intent_labels == active_intent_preds) / len(active_intent_labels)

    # joint_acc, turn_acc = \
    #     evaluate_metrics(global_vars['comp_res'],
    #                      global_vars['gating_labels'],
    #                      global_vars['gating_preds'],
    #                      data_desc.gating_dict["ptr"])

    # gating_comp_flatten = (np.asarray(global_vars['gating_labels']) == np.asarray(global_vars['gating_preds'])).ravel()
    # gating_acc = np.sum(gating_comp_flatten) / len(gating_comp_flatten)
    metrics = {'all_services':
        {
        "active_intent_accuracy": active_intent_accuracy,
        # "average_cat_accuracy": 0.673011948908117,
        # "average_goal_accuracy": 0.763325453086777,
        # "average_noncat_accuracy": 0.7997492378543167,
        # "joint_cat_accuracy": 0.7009794862317501,
        # "joint_goal_accuracy": 0.4904726693494299,
        # "joint_noncat_accuracy": 0.6226867035546613,
        # "requested_slots_f1": 0.9586998179553512,
        # "requested_slots_precision": 0.988388665325285,
        # "requested_slots_recall": 0.960093896713615
            }
        }
    print(metrics)



    # active_intent_acc = metrics.get_active_intent_accuracy(
    #         frame_ref, frame_hyp)
    # slot_tagging_f1_scores = metrics.get_slot_tagging_f1(
    #     frame_ref, frame_hyp, turn_ref["utterance"], service)
    # requested_slots_f1_scores = metrics.get_requested_slots_f1(
    #     frame_ref, frame_hyp)
    # goal_accuracy_dict = metrics.get_average_and_joint_goal_accuracy(
    #     frame_ref, frame_hyp, service)

    return metrics


def evaluate_metrics(comp_res, gating_labels, gating_preds, ptr_code):
    # TODO: Calculate precision, recall, and F1
    total_slots = 0
    correct_slots = 0
    total_turns = 0
    correct_turns = 0
    for result_idx, result in enumerate(comp_res):
        turn_wrong = False
        total_turns += 1
        for slot_idx, slot_eq in enumerate(result):
            total_slots += 1
            if gating_labels[result_idx][slot_idx] == ptr_code:
                if slot_eq:
                    correct_slots += 1
                else:
                    turn_wrong = True
            elif gating_labels[result_idx][slot_idx] == gating_preds[result_idx][slot_idx] \
                    or (slot_eq and gating_preds[result_idx][slot_idx] == ptr_code):
                correct_slots += 1
            else:
                turn_wrong = True
        if not turn_wrong:
            correct_turns += 1

    turn_acc = correct_slots / float(total_slots) if total_slots != 0 else 0
    joint_acc = correct_turns / float(total_turns) if total_turns != 0 else 0
    return joint_acc, turn_acc


F1Scores = collections.namedtuple("F1Scores", ["f1", "precision", "recall"])

def compute_f1(list_ref, list_hyp):
  """Compute F1 score from reference (grouth truth) list and hypothesis list.

  Args:
    list_ref: List of true elements.
    list_hyp: List of postive (retrieved) elements.

  Returns:
    A F1Scores object containing F1, precision, and recall scores.
  """

  ref = collections.Counter(list_ref)
  hyp = collections.Counter(list_hyp)
  true = sum(ref.values())
  positive = sum(hyp.values())
  true_positive = sum((ref & hyp).values())
  precision = float(true_positive) / positive if positive else 1.0
  recall = float(true_positive) / true if true else 1.0
  if precision + recall > 0.0:
    f1 = 2.0 * precision * recall / (precision + recall)
  else:  # The F1-score is defined to be 0 if both precision and recall are 0.
    f1 = 0.0

  return F1Scores(f1=f1, precision=precision, recall=recall)